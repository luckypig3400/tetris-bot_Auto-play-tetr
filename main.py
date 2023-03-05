import pyautogui
import cv2
import tkinter
from tkinter import messagebox

# Define the colors of the Tetris blocks
colors = {
    (85, 255, 255): "-",  # yellow
    (255, 0, 0): "-",    # blue
    (0, 255, 0): "-",    # green
    (255, 85, 85): "-",  # red
    (255, 255, 0): "-",  # light blue
    (255, 165, 0): "-",  # orange
    (128, 0, 128): "-",  # purple
}

# Initialize the capture region
region = None

# Define the function to capture the screen region
def capture_region():
    global region

    root = tkinter.Tk()
    root.withdraw()

    messagebox.showinfo("Capture Region", "Select the region of the screen to capture")

    # Capture the screen to get the screen dimensions
    screen = pyautogui.screenshot()

    # Create a fullscreen window with no decorations
    fullscreen = tkinter.Toplevel()
    fullscreen.overrideredirect(True)
    fullscreen.geometry("{0}x{1}+0+0".format(screen.width, screen.height))
    fullscreen.focus_set()
    fullscreen.bind("<Escape>", lambda _: fullscreen.quit())

    # Create an adjustable selection overlay on the screen
    canvas = tkinter.Canvas(fullscreen, bg="black", highlightthickness=0)
    canvas.pack(fill="both", expand=True)

    # Create the selection rectangle
    selection = canvas.create_rectangle(0, 0, 0, 0, outline="red")

    # Define the function to update the selection rectangle
    def update_selection(event):
        nonlocal selection
        x, y = canvas.canvasx(event.x), canvas.canvasy(event.y)
        canvas.coords(selection, anchor_x, anchor_y, x, y)

    # Define the function to set the capture region
    def set_region():
        global region
        region = (anchor_x, anchor_y, selection_x, selection_y)
        messagebox.showinfo("Capture Region", "Capture region set successfully")
        fullscreen.quit()

    # Bind the mouse events
    def start_selection(event):
        nonlocal anchor_x, anchor_y
        anchor_x, anchor_y = canvas.canvasx(event.x), canvas.canvasy(event.y)

        canvas.bind("<B1-Motion>", update_selection)
        canvas.bind("<ButtonRelease-1>", end_selection)

    def end_selection(event):
        nonlocal selection_x, selection_y
        selection_x, selection_y = canvas.coords(selection)[2:]

        canvas.unbind("<B1-Motion>")
        canvas.unbind("<ButtonRelease-1>")

        set_region()

    canvas.bind("<ButtonPress-1>", start_selection)

    # Start the event loop
    fullscreen.mainloop()

# Define the function to process the captured image
def process_image():
    if region is None:
        messagebox.showerror("Error", "Please select a capture region first")
        return

    # Capture the region of the screen
    img = pyautogui.screenshot(region=region)

    # Convert the image to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Threshold the image to create a binary image
    _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)

    # Find the contours of the blocks
    contours, _ = cv2.findContours(
        thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Initialize the block status list
    block_status = []

    # Loop through each contour
    for contour in contours:
        # Get the area and perimeter of the contour
        area = cv2.contourArea(contour)
        perimeter = cv2.arcLength(contour, True)

        # Calculate the circularity of the contour
        if perimeter == 0:
            circularity = 0
        else:
            circularity = 4 * math.pi * area / perimeter ** 2

        # If the circularity is high enough, the contour is a block
        if circularity > 0.7:
            # Get the bounding box of the block
            x, y, w, h = cv2.boundingRect(contour)

            # Crop the block from the image
            block_img = gray[y:y+h, x:x+w]

            # Resize the block to a fixed size
            block_img = cv2.resize(block_img, (20, 20))

            # Calculate the mean color of the block
            mean_color = cv2.mean(img[y:y+h, x:x+w])[0:3]

            # Determine the type of block based on the color
            if mean_color in colors:
                block_type = colors[mean_color]
            else:
                block_type = "?"

            # Add the block to the block status list
            block_status.append(block_type)
        else:
            continue

    # Print the block status to the console
    for i in range(20):
        row = ""
        for j in range(10):
            if j * 20 + i < len(block_status):
                row += block_status[j * 20 + i]
            else:
                row += " "
        print(row)

# Ask User the tetris game region at script start
capture_region()

# Loop indefinitely
while True:
    process_image()