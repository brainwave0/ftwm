use std::error::Error;
use xcb::{
    x::{Screen, Window},
    Connection,
};
pub fn screen<'a>(connection: &'a Connection) -> Result<&'a Screen, &'static str> {
    connection
        .get_setup()
        .roots()
        .next()
        .ok_or("Couldn't get screen")
}
pub fn root(connection: &Connection) -> Result<Window, Box<dyn Error>> {
    Ok(screen(&connection)?.root())
}
pub fn screen_center(connection: &Connection) -> Result<(u16, u16), Box<dyn Error>> {
    let screen = screen(&connection)?;
    Ok((screen.width_in_pixels() / 2, screen.height_in_pixels() / 2))
}
