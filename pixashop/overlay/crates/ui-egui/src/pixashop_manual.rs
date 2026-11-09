//! A bundled, searchable PixaShop guide. Reading it never requires network access.
use serde::Deserialize;
use std::sync::OnceLock;
const ONLINE: &str = "https://aiwebdesignfirm.com/pixashop/manual";
#[derive(Deserialize)]
struct Guide { edition: String, sections: Vec<Chapter> }
#[derive(Deserialize)]
struct Chapter { id: String, title: String, intro: String, steps: Vec<String>, note: String }
fn key() -> egui::Id { egui::Id::new("pixashop-user-manual") }
pub(crate) fn open(ctx: &egui::Context) { ctx.data_mut(|d| d.insert_temp(key(), true)); }
fn guide() -> &'static Result<Guide, String> {
    static GUIDE: OnceLock<Result<Guide, String>> = OnceLock::new();
    GUIDE.get_or_init(|| serde_json::from_str(include_str!("../../../pixashop/manual/guide.json")).map_err(|e| e.to_string()))
}
pub(crate) fn show(app: &mut crate::PhotocraftApp, ctx: &egui::Context) {
    let mut visible = ctx.data(|d| d.get_temp::<bool>(key())).unwrap_or(false);
    if !visible { return; }
    let search_key = key().with("search");
    let mut search = ctx.data(|d| d.get_temp::<String>(search_key)).unwrap_or_default();
    let mut online = false;
    egui::Window::new("PixaShop User Manual").open(&mut visible).default_size(egui::vec2(760.0, 620.0)).resizable(true).show(ctx, |ui| {
        ui.heading("PixaShop");
        ui.weak("by AIWebDesignFirm · Your vision. Down to the pixel.");
        ui.horizontal_wrapped(|ui| {
            ui.label("This guide is included in your app.");
            online = ui.link("Open online manual").clicked();
        });
        ui.add_space(8.0);
        ui.add(egui::TextEdit::singleline(&mut search).hint_text("Search chapters, tools, or tasks…").desired_width(f32::INFINITY));
        ui.separator();
        match guide() {
            Err(_) => { ui.label("The bundled guide could not be read. Open the online manual above."); }
            Ok(guide) => {
                ui.weak(format!("Guide edition {} · Click a chapter to read it", guide.edition));
                let query = search.trim().to_lowercase();
                let mut matches = 0;
                egui::ScrollArea::vertical().id_salt("pixashop-guide-chapters").show(ui, |ui| {
                    for (i, chapter) in guide.sections.iter().enumerate() {
                        let haystack = format!("{} {} {} {}", chapter.title, chapter.intro, chapter.steps.join(" "), chapter.note).to_lowercase();
                        if !query.is_empty() && !haystack.contains(&query) { continue; }
                        matches += 1;
                        egui::CollapsingHeader::new(format!("{:02}  {}", i+1, chapter.title)).id_salt(&chapter.id).default_open(!query.is_empty()).show(ui, |ui| {
                            ui.add(egui::Label::new(&chapter.intro).wrap());
                            ui.add_space(8.0);
                            for (step, text) in chapter.steps.iter().enumerate() {
                                ui.add(egui::Label::new(format!("{}. {}", step+1, text)).wrap());
                                ui.add_space(8.0);
                            }
                            ui.add(egui::Label::new(egui::RichText::new(&chapter.note).weak()).wrap());
                            ui.add_space(12.0);
                        });
                    }
                    if matches == 0 { ui.label("No chapters match. Try a tool name, such as layers, text, or export."); }
                });
            }
        }
    });
    ctx.data_mut(|d| { d.insert_temp(key(), visible); d.insert_temp(search_key, search); });
    if online { crate::links::open(app, ctx, ONLINE); }
}
#[cfg(test)]
mod tests {
    #[test]
    fn help_manual_opens_without_a_document() {
        let mut app = crate::PhotocraftApp::new(photocraft_engine::Session::new(), Default::default());
        let ctx = egui::Context::default();
        assert!(crate::menus::is_live("help.manual"));
        assert!(crate::menus::is_enabled(&app, "help.manual"));
        crate::menus::invoke(&mut app, &ctx, "help.manual", serde_json::json!({})).unwrap();
        assert_eq!(ctx.data(|d| d.get_temp::<bool>(super::key())), Some(true));
        let guide = super::guide().as_ref().unwrap();
        assert!(guide.sections.iter().any(|s| s.id == "first-edit"));
        assert!(guide.sections.iter().any(|s| s.id == "updates"));
    }
}
