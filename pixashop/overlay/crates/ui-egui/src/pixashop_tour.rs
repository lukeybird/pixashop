//! A read-only, tool-by-tool tour. Navigation never invokes an editing command.
use crate::{PhotocraftApp, state::Tool};
use egui::{Context, Id, Rect, Stroke};
use serde::Deserialize;
use std::sync::OnceLock;

#[derive(Deserialize)]
struct Step {
    id: String,
    title: String,
    description: String,
    try_it: String,
}
#[derive(Clone, Default)]
struct Tour {
    open: bool,
    index: usize,
    anchors: Vec<(Tool, Rect)>,
}
fn key() -> Id {
    Id::new("pixashop-tool-tour")
}
fn steps() -> &'static Result<Vec<Step>, String> {
    static STEPS: OnceLock<Result<Vec<Step>, String>> = OnceLock::new();
    STEPS.get_or_init(|| serde_json::from_str(include_str!("../../../pixashop/manual/tools.json")).map_err(|e| e.to_string()))
}
pub(crate) fn open(ctx: &Context) {
    crate::pixashop_manual::close(ctx);
    ctx.data_mut(|d| d.insert_temp(key(), Tour { open: true, ..Default::default() }));
}
pub(crate) fn begin_frame(ctx: &Context) {
    ctx.data_mut(|d| {
        if let Some(mut tour) = d.get_temp::<Tour>(key()) {
            tour.anchors.clear();
            d.insert_temp(key(), tour);
        }
    });
}
pub(crate) fn note_slot(ui: &mut egui::Ui, slot: &[Tool], rect: Rect) {
    let ctx = ui.ctx().clone();
    let tour = ctx.data(|d| d.get_temp::<Tour>(key()));
    if let Some(tour) = &tour {
        if tour.open && !ui.is_rect_visible(rect) {
            let target = steps().as_ref().ok().and_then(|all| all.get(tour.index)).and_then(|step| crate::tool_shortcuts::tool(&step.id));
            if target.is_some_and(|tool| slot.contains(&tool)) {
                ui.scroll_to_rect(rect, Some(egui::Align::Center));
            }
        }
    }
    if !ui.is_rect_visible(rect) {
        return;
    }
    ctx.data_mut(|d| {
        if let Some(mut tour) = d.get_temp::<Tour>(key()) {
            if tour.open {
                tour.anchors.extend(slot.iter().copied().map(|t| (t, rect)));
                d.insert_temp(key(), tour);
            }
        }
    });
}
fn bounded_index(index: usize, len: usize) -> usize {
    index.min(len.saturating_sub(1))
}

pub(crate) fn show(app: &mut PhotocraftApp, ctx: &Context) {
    let mut tour = ctx.data(|d| d.get_temp::<Tour>(key())).unwrap_or_default();
    if !tour.open {
        return;
    }
    if ctx.input(|i| i.key_pressed(egui::Key::Escape)) {
        tour.open = false;
        ctx.data_mut(|d| d.insert_temp(key(), tour));
        return;
    }
    let Ok(steps) = steps() else {
        egui::Window::new("PixaShop tool tour").open(&mut tour.open).show(ctx, |ui| {
            ui.label("The tool guide could not be read. Open Help → PixaShop User Manual instead.");
        });
        ctx.data_mut(|d| d.insert_temp(key(), tour));
        return;
    };
    tour.index = bounded_index(tour.index, steps.len());
    let Some(step) = steps.get(tour.index) else {
        return;
    };
    let target = crate::tool_shortcuts::tool(&step.id);
    let anchor = target.and_then(|t| tour.anchors.iter().find(|(tool, _)| *tool == t).map(|(_, rect)| *rect));
    let screen = ctx.content_rect();
    let width = (screen.width() - 56.0).clamp(180.0, 370.0);
    let desired = anchor.map(|r| egui::pos2(r.right() + 18.0, r.top() - 16.0)).unwrap_or(screen.left_top() + egui::vec2(24.0, 76.0));
    let pos = egui::pos2(
        desired.x.max(screen.left() + 12.0).min((screen.right() - width - 44.0).max(screen.left() + 12.0)),
        desired.y.max(screen.top() + 12.0).min((screen.bottom() - 430.0).max(screen.top() + 12.0)),
    );
    let tokens = crate::theme::Tokens::get(ctx);
    let accent = tokens.accent;
    if let Some(rect) = anchor {
        let painter = ctx.layer_painter(egui::LayerId::new(egui::Order::Foreground, key().with("highlight")));
        painter.rect_stroke(rect.expand(3.0), 5.0, Stroke::new(2.0, accent), egui::StrokeKind::Outside);
        let from = rect.right_center();
        let to = egui::pos2(pos.x, pos.y + 42.0);
        painter.line_segment([from, to], Stroke::new(1.5, accent));
        painter.circle_filled(from, 3.0, accent);
    }
    let mut go_back = false;
    let mut go_next = false;
    let mut open_manual = false;
    egui::Window::new("PixaShop quick tool tour").id(key().with("bubble")).title_bar(false).collapsible(false).resizable(false).movable(false)
        .fixed_pos(pos).default_width(width).frame(egui::Frame::popup(&ctx.style()).inner_margin(16).corner_radius(12))
        .show(ctx, |ui| {
            ui.horizontal(|ui| {
                ui.strong("PixaShop · Quick tool tour");
                if ui.small_button("Skip").clicked() { tour.open = false; }
            });
            ui.weak(format!("Tool {} of {} · Your image is not changed by the tour", tour.index+1, steps.len()));
            ui.add_space(8.0);
            egui::ComboBox::from_id_salt("pixashop-tour-tool-picker").selected_text(&step.title).width(width-44.0).show_ui(ui, |ui| {
                for (index, item) in steps.iter().enumerate() { ui.selectable_value(&mut tour.index, index, &item.title); }
            });
            egui::ScrollArea::vertical().max_height((screen.height()-220.0).clamp(120.0, 310.0)).show(ui, |ui| {
                ui.add_space(10.0);
                ui.add(egui::Label::new(&step.description).wrap());
                ui.add_space(10.0);
                ui.strong("How to use it");
                ui.add(egui::Label::new(&step.try_it).wrap());
                if let Some(tool) = target {
                    if let Some(shortcut) = crate::tool_shortcuts::shortcut(app, tool) {
                        ui.weak(format!("Shortcut: {}", crate::shortcuts::pretty(&shortcut)));
                    }
                }
                ui.add_space(10.0);
                if anchor.is_some() {
                    ui.add(egui::Label::new(egui::RichText::new("The outline marks this tool’s group. Right-click its toolbar icon to find tools in the flyout.").weak()).wrap());
                } else {
                    ui.add(egui::Label::new(egui::RichText::new("Open an image or create a document to see toolbar highlights. Scroll the toolbox if needed. For a hidden tool, look in the toolbar flyout or Edit → Toolbar.").weak()).wrap());
                }
            });
            ui.add_space(10.0);
            ui.horizontal(|ui| {
                go_back = ui.add_enabled(tour.index > 0, egui::Button::new("← Back")).clicked();
                go_next = ui.button(if tour.index+1 == steps.len() { "Done ✓" } else { "Next →" }).clicked();
                open_manual = ui.small_button("Manual").clicked();
            });
            ui.add_space(6.0);
            ui.add(egui::ProgressBar::new((tour.index+1) as f32 / steps.len() as f32).fill(accent).desired_height(3.0));
        });
    if go_back {
        tour.index = tour.index.saturating_sub(1);
    }
    if go_next {
        if tour.index + 1 >= steps.len() {
            tour.open = false;
        } else {
            tour.index += 1;
        }
    }
    if open_manual {
        crate::pixashop_manual::open(ctx);
        tour.open = false;
    }
    ctx.data_mut(|d| d.insert_temp(key(), tour));
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn tour_covers_every_registered_tool_once() {
        let steps = steps().as_ref().unwrap();
        let mut ids: Vec<_> = steps.iter().map(|s| s.id.as_str()).collect();
        ids.sort_unstable();
        let count = ids.len();
        ids.dedup();
        assert_eq!(count, ids.len());
        let mut tools: Vec<_> = photocraft_engine::shell_commands::TOOLS.iter().map(|t| t.0).collect();
        tools.sort_unstable();
        assert_eq!(ids, tools);
        for step in steps {
            assert!(crate::tool_shortcuts::tool(&step.id).is_some());
            assert!(!step.description.is_empty() && !step.try_it.is_empty());
        }
    }
    #[test]
    fn opening_and_navigation_do_not_change_the_active_tool_or_documents() {
        let mut app = PhotocraftApp::new(photocraft_engine::Session::new(), Default::default());
        let ctx = Context::default();
        let before = app.ui.tool;
        assert!(crate::menus::is_enabled(&app, "help.toolTour"));
        crate::menus::invoke(&mut app, &ctx, "help.toolTour", serde_json::json!({})).unwrap();
        assert!(ctx.data(|d| d.get_temp::<Tour>(key())).unwrap().open);
        assert_eq!(app.ui.tool, before);
        assert!(app.session.active().is_none());
        let output = ctx.run(egui::RawInput::default(), |ctx| show(&mut app, ctx));
        assert!(!output.shapes.is_empty(), "the tour must render without a document");
        assert_eq!(app.ui.tool, before);
        assert_eq!(bounded_index(usize::MAX, steps().as_ref().unwrap().len()), steps().as_ref().unwrap().len() - 1);
        assert_eq!(bounded_index(1, 0), 0);
    }
}
