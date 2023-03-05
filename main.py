import pyautogui
import cv2
import tkinter as tk
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

    # Hide the main window
    root.withdraw()

    # Display the overlay window
    overlay = tk.Toplevel()
    overlay.attributes("-fullscreen", True)
    overlay.attributes("-alpha", 0.5)
    overlay.attributes("-topmost", True)
    overlay.configure(bg="black")

    # Add a label to the overlay window
    label = tk.Label(overlay, text="Drag and resize the box to select the capture region", font=(
        "Arial", 16), fg="white", bg="black")
    label.pack(side="top", padx=10, pady=10)

    # Add a canvas to the overlay window
    canvas = tk.Canvas(overlay, bg="black", highlightthickness=0)
    canvas.pack(fill="both", expand=True)

    # Define the rectangle for the capture region
    x, y, w, h = pyautogui.position()
    rect = canvas.create_rectangle(x, y, x+w, y+h, outline="white")

    # Define the function to update the rectangle
    def update_rect(event):
        nonlocal x, y, w, h
        x, y = canvas.canvasx(event.x), canvas.canvasy(event.y)
        w, h = event.x - canvas.canvasx(rect), event.y - canvas.canvasy(rect)
        canvas.coords(rect, x, y, x+w, y+h)

    # Bind the events to the canvas
    canvas.bind("<B1-Motion>", update_rect)
    canvas.bind("<ButtonRelease-1>", overlay.quit)

    # Start the event loop for the overlay window
    overlay.mainloop()

    # Show the main window
    root.deiconify()

    # Set the capture region
    region = (x, y, w, h)

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
