use face_detect::FaceDetector;
use opencv::{
    core::{Mat, flip},
    prelude::{MatTraitConst, VideoCaptureTrait},
    videoio::{VideoCapture, CAP_ANY},
};
use std::error::Error;
use xcb::{
    x::{
        ChangeWindowAttributes, ConfigWindow, ConfigureWindow,
        ReparentWindow, Window, Screen, MapWindow, GetGeometry, Drawable
    },
    Connection,
};
fn screen<'a>(connection: &'a Connection) -> Result<&'a Screen, &'static str> {
    connection.get_setup().roots().next().ok_or("Couldn't get screen")
}
fn root(connection: &Connection) -> Result<Window, Box<dyn Error>> {
    Ok(screen(&connection)?.root())
}
fn screen_center(connection: &Connection) -> Result<(u32, u32), Box<dyn Error>> {
    let screen = screen(&connection)?;
    Ok((screen.width_in_pixels() / 2, screen.height_in_pixels() / 2))
}
fn pan_window(
    connection: &Connection,
    window: Window,
    delta: (i32, i32),
) -> Result<(), Box<dyn Error>> {
    let cookie = connection.send_request(&GetGeometry {drawable: Drawable::Window(window)});
    let reply = connection.wait_for_reply(cookie)?;
    connection.send_request(&ConfigureWindow {
        window: window,
        value_list: &[
            ConfigWindow::X(screen_center(&connection)?.0 + delta.0 - reply.width() / 2),
            ConfigWindow::Y(screen_center(&connection)?.1 + delta.1 - reply.height() / 2),
        ],
    });
    Ok(())
}
fn reparent(connection: &Connection, window: Window, windows: &mut Vec<Window>) -> Result<(), Box<dyn Error>> {
    connection.send_request(&ReparentWindow {
        window: window,
        parent: root(connection)?,
        x: 0,
        y: 0,
    });
    Ok(())
}
fn handle_map_request(connection: &Connection, windows: &mut Vec<Window>, window: Window) {
    connection.send_request(&MapWindow {
        window: window,
    });
    windows.push(window);
}
fn handle_events(
    connection: &Connection,
    windows: &mut Vec<Window>,
) -> Result<(), Box<dyn Error>> {
    if let Some(event) = connection.poll_for_event()? {
        match event {
            xcb::Event::X(x_event) => match x_event {
                xcb::x::Event::MapRequest(mr_event) => 
                    handle_map_request(connection, windows, mr_event.window()),
                
                other_event => (),
            },
            xcb::Event::Unknown(_) => (),
        }
    }
    Ok(())
}
fn pan(
    connection: &Connection,
    frame: &Mat,
    face_detector: &mut FaceDetector,
    windows: &Vec<Window>,
) -> Result<(), Box<dyn Error>> {
    let frame_center = (frame.cols() / 2, frame.rows() / 2);
    let face_rectangle = face_detector.detect_face(frame)?;
    let face_center = (
        face_rectangle.x + face_rectangle.width / 2,
        face_rectangle.y + face_rectangle.height / 2,
    );
    let face_delta = (
        face_center.0 - frame_center.0,
        face_center.1 - frame_center.1,
    );
    let delta = (face_delta.0 * 7, face_delta.1 * 8);
    for window in windows {
        pan_window(connection, *window, delta)?;
    }
    Ok(())
}
fn register_wm(connection: &Connection) -> Result<(), Box<dyn Error>> {
    let mut flags = xcb::x::EventMask::empty();
    flags.insert(xcb::x::EventMask::PROPERTY_CHANGE);
    flags.insert(xcb::x::EventMask::STRUCTURE_NOTIFY);
    flags.insert(xcb::x::EventMask::SUBSTRUCTURE_NOTIFY);
    flags.insert(xcb::x::EventMask::SUBSTRUCTURE_REDIRECT);
    connection.send_request(&ChangeWindowAttributes {
        window: root(connection)?,
        value_list: &[
            xcb::x::Cw::EventMask(flags)
        ],
    });
    Ok(())
}
fn smooth(elements: Vec<u32>) -> u32 {

}
fn main() -> Result<(), Box<dyn Error>> {
    let mut frame = Mat::default(); // Create an OpenCV matrix to store the frame.
    let mut video_capture = VideoCapture::new(0, CAP_ANY).expect("Couldn't open webcam."); // Create a new VideoCapture instance using CAP_ANY to auto-detect the backend.
    let (connection, _) = Connection::connect(None)?;
    let mut face_detector = FaceDetector::new()?;
    let mut windows = Vec::new();
    let mut buffer = Vec::new();
    register_wm(&connection)?;
    loop {
        video_capture
            .read(&mut frame)
            .expect("Couldn't get frame from webcam."); // Capture a frame and put it in the frame container.

        let mut tmp = Mat::default();
        flip(&frame, &mut tmp, 0)?;
        frame = tmp;

        handle_events(&connection, &mut windows)?;
        pan(&connection, &frame, &mut face_detector, &windows)?;
        connection.flush()?;
    }
}
