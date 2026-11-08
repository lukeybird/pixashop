//! Own-repository release notifications. No upstream installer can replace PixaShop.
use crate::PhotocraftApp;
use photocraft_engine::updates_cmds::Status;
use serde_json::Value;
#[derive(Default)]
pub(crate) struct Runtime {
    startup_checked: bool,
    notified_version: Option<String>,
    #[cfg(target_os = "macos")]
    pending: Option<std::sync::mpsc::Receiver<Result<crate::pixashop_updater::Prepared, String>>>,
    #[cfg(target_os = "macos")]
    ready: Option<crate::pixashop_updater::Prepared>,
    message: String,
}
pub(crate) fn check(app: &mut PhotocraftApp, _ctx: &egui::Context, params: Value) -> Result<Value, String> {
    app.ui.updates_open = true;
    app.updates_rt.startup_checked = true;
    app.run("help.checkForUpdates", params)
}
pub(crate) fn tick(app: &mut PhotocraftApp, ctx: &egui::Context) {
    app.session.updates.poll();
    if let Status::Available { release } = &app.session.updates.status {
        if app.updates_rt.notified_version.as_ref() != Some(&release.version) {
            app.updates_rt.notified_version = Some(release.version.clone());
            app.ui.updates_open = true;
        }
    }
    if !app.updates_rt.startup_checked && app.session.updates.check.is_some() {
        app.updates_rt.startup_checked = true;
        if app.session.prefs().general.automatically_check_updates {
            let _ = app.run("help.checkForUpdates", serde_json::json!({}));
        }
    }
    if matches!(app.session.updates.status, Status::Checking) {
        ctx.request_repaint_after(std::time::Duration::from_millis(100));
    }
}
pub(crate) fn show(app: &mut PhotocraftApp, ctx: &egui::Context) {
    #[cfg(target_os = "macos")]
    {
        if let Some(rx) = &app.updates_rt.pending {
            let result = match rx.try_recv() {
                Ok(result) => Some(result),
                Err(std::sync::mpsc::TryRecvError::Empty) => None,
                Err(std::sync::mpsc::TryRecvError::Disconnected) => Some(Err("The update stopped. Please try again.".into())),
            };
            if let Some(result) = result {
                app.updates_rt.pending = None;
                match result {
                    Ok(ready) => app.updates_rt.ready = Some(ready),
                    Err(error) => app.updates_rt.message = error,
                }
            }
            ctx.request_repaint_after(std::time::Duration::from_millis(100));
        }
        if app.updates_rt.ready.is_some() && !app.has_unsaved_work() {
            if let Some(ready) = app.updates_rt.ready.take() {
                match crate::pixashop_updater::restart(ready) {
                    Ok(()) => ctx.send_viewport_cmd(egui::ViewportCommand::Close),
                    Err(error) => app.updates_rt.message = error,
                }
            }
        }
    }
    if !app.ui.updates_open {
        return;
    }
    let clean = !app.has_unsaved_work();
    let mut install_version: Option<String> = None;
    let mut open = true;
    let mut again = false;
    egui::Window::new("PixaShop updates").open(&mut open).show(ctx, |ui| {
        ui.label("by AIWebDesignFirm");
        match &app.session.updates.status {
            Status::Available { release } => {
                ui.label(format!("PixaShop {} is available.", release.version));
                #[cfg(target_os = "macos")]
                {
                    let busy = app.updates_rt.pending.is_some() || app.updates_rt.ready.is_some();
                    if busy {
                        ui.spinner();
                        ui.label("Downloading and verifying your update…");
                    }
                    if !clean {
                        ui.label("Save or close your open work before installing and restarting.");
                    }
                    if app.updates_rt.ready.is_some() {
                        ui.label("Update verified. Waiting for you to save your work.");
                    }
                    if ui.add_enabled(clean && !busy, egui::Button::new("Install and restart")).clicked() {
                        install_version = Some(release.version.clone());
                    }
                }
                #[cfg(not(target_os = "macos"))]
                ui.label("In-app installation is currently available on Mac. Install the latest version from our website on this platform.");
                #[cfg(not(target_os = "macos"))]
                if ui.button("Download update").clicked() {
                    // Fixed publisher domain: release metadata never supplies an executable URL.
                    ctx.open_url(egui::OpenUrl::new_tab("https://aiwebdesignfirm.com/pixashop"));
                }
            }
            Status::Checking => {
                ui.spinner();
                ui.label("Checking for updates…");
            }
            Status::UpToDate => {
                ui.label("You have the latest published PixaShop version.");
            }
            Status::Failed { message } => {
                ui.label(message);
            }
            Status::Idle => {
                ui.label("Check for a new PixaShop release.");
            }
        }
        if !app.updates_rt.message.is_empty() {
            ui.label(&app.updates_rt.message);
        }
        if ui.button("Check again").clicked() {
            again = true;
        }
    });
    #[cfg(target_os = "macos")]
    if let Some(version) = install_version {
        let (tx, rx) = std::sync::mpsc::channel();
        app.updates_rt.message.clear();
        match std::thread::Builder::new().name("PixaShop installer".into()).spawn(move || {
            let _ = tx.send(crate::pixashop_updater::prepare(&version));
        }) {
            Ok(_) => app.updates_rt.pending = Some(rx),
            Err(error) => app.updates_rt.message = format!("Could not start update: {error}"),
        }
    }
    #[cfg(not(target_os = "macos"))]
    let _ = (clean, &mut install_version);
    app.ui.updates_open = open;
    if again {
        let _ = check(app, ctx, serde_json::json!({}));
    }
}
