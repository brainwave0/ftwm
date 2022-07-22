use std::error::Error;
use xcb::{
    x::{MapWindow, Window, ConfigureWindow, ConfigWindow},
    Connection,
};
fn handle_map_request(connection: &Connection, windows: &mut Vec<Window>, window: Window) {
    connection.send_request(&ConfigureWindow {
        window: window,
        value_list: &[
            ConfigWindow::Width(
                1920
            ),
            ConfigWindow::Height(
                1080
            ),
        ],
    });
    connection.send_request(&MapWindow { window: window });
    windows.push(window);
}
pub fn handle_events(
    connection: &Connection,
    windows: &mut Vec<Window>,
) -> Result<(), Box<dyn Error>> {
    if let Some(event) = connection.poll_for_event()? {
        match event {
            xcb::Event::X(x_event) => match x_event {
                xcb::x::Event::MapRequest(mr_event) => {
                    handle_map_request(connection, windows, mr_event.window())
                }

                _ => (),
            },
            xcb::Event::Unknown(_) => (),
        }
    }
    Ok(())
}
