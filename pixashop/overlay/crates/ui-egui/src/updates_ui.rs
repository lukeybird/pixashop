//! Own-repository release notifications. No upstream installer can replace PixaShop.
use photocraft_engine::updates_cmds::Status;
use serde_json::Value;
use crate::PhotocraftApp;
#[derive(Default)]
pub(crate) struct Runtime { startup_checked: bool, notified_version: Option<String> }
pub(crate) fn check(app: &mut PhotocraftApp, _ctx: &egui::Context, params: Value) -> Result<Value, String> {
    app.ui.updates_open = true; app.updates_rt.startup_checked = true;
    app.run("help.checkForUpdates", params)
}
pub(crate) fn tick(app: &mut PhotocraftApp, ctx: &egui::Context) {
    app.session.updates.poll();
    if let Status::Available { release } = &app.session.updates.status {
        if app.updates_rt.notified_version.as_ref() != Some(&release.version) {
            app.updates_rt.notified_version = Some(release.version.clone()); app.ui.updates_open = true;
        }
    }
    if !app.updates_rt.startup_checked && app.session.updates.check.is_some() {
        app.updates_rt.startup_checked = true;
        if app.session.prefs().general.automatically_check_updates { let _ = app.run("help.checkForUpdates", serde_json::json!({})); }
    }
    if matches!(app.session.updates.status, Status::Checking) { ctx.request_repaint_after(std::time::Duration::from_millis(100)); }
}
pub(crate) fn show(app: &mut PhotocraftApp, ctx: &egui::Context) {
    if !app.ui.updates_open { return; }
    let mut open = true; let mut again = false;
    egui::Window::new("PixaShop updates").open(&mut open).show(ctx, |ui| {
        ui.label("by AIWebDesignFirm");
        match &app.session.updates.status {
            Status::Available { release } => {
                ui.label(format!("PixaShop {} is available.", release.version));
                ui.label("Save your work, download the new installer and install it over your current version.");
                if ui.button("Download update").clicked() {
                    // Fixed publisher domain: release metadata never supplies an executable URL.
                    ctx.open_url(egui::OpenUrl::new_tab("https://aiwebdesignfirm.com/pixashop"));
                }
            }
            Status::Checking => { ui.spinner(); ui.label("Checking for updates…"); }
            Status::UpToDate => { ui.label("You have the latest published PixaShop version."); }
            Status::Failed { message } => { ui.label(message); }
            Status::Idle => { ui.label("Check for a new PixaShop release."); }
        }
        if ui.button("Check again").clicked() { again = true; }
    });
    app.ui.updates_open = open;
    if again { let _ = check(app, ctx, serde_json::json!({})); }
}
