//! PixaShop checks only its own releases. Installation uses the platform installer.
use photocraft_engine::updates_cmds::{CheckFn, CheckResult};
pub fn service() -> CheckFn {
    Box::new(|| {
        let (tx, rx) = std::sync::mpsc::channel();
        std::thread::Builder::new().name("PixaShop updates".into()).spawn(move || { let _ = tx.send(check()); })
            .map_err(|_| "Could not start the update check".to_string())?;
        Ok(rx)
    })
}
fn check() -> CheckResult {
    let http = craft_update::Http::new("PixaShop/Update")?;
    match http.get_api("https://api.github.com/repos/lukeybird/pixashop/releases/latest", None)? {
        craft_update::http::Fetched::Body { text, .. } => photocraft_engine::updates_cmds::parse_release(text.as_bytes(), photocraft_engine::build_info::VERSION),
        craft_update::http::Fetched::NotFound | craft_update::http::Fetched::NotModified => Ok(None),
        craft_update::http::Fetched::RateLimited { .. } => Err("Update checks are temporarily rate limited. Try again later.".into()),
    }
}
