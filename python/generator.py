# Created for setting up physical device against screen
import barcode
from barcode.writer import ImageWriter
from io import BytesIO
from barcode import generate
import config
from PIL import Image, ImageTk
import tkinter as tk
import os


# Generating barcode using barcode
def generate_barcode(tenam):
    ean = barcode.get_barcode_class('code128')
    my_ean = ean(tenam, writer=ImageWriter())
    fp = BytesIO()
    my_ean.write(fp)
    code128 = barcode.get_barcode_class('code128')
    my_ean13 = code128(tenam, writer=ImageWriter())
    my_ean13.save(config.barcodes_path_dc2 + '\\' + tenam)
    generate('code128', tenam, writer=ImageWriter(), output=fp)


# Showing generated barcode using tk
def show_image(image_path, x, y, duration=None):
    root = tk.Tk()
    root.geometry("+{}+{}".format(x, y))

    image = Image.open(image_path)
    photo = ImageTk.PhotoImage(image)

    label = tk.Label(root, image=photo)
    label.image = photo
    label.pack()

    if duration:
        root.after(duration * 1000, root.destroy)

    root.mainloop()


print("TIP: -25, 700 will be bottom-corner of the screen")
CoordinatesX = int(input("Set X-axis coordinates for test: "))
CoordinatesY = int(input("Set Y-axis coordinates for test: "))
Timer = int(input("Set displaying time: "))
Code = str(input("Enter number to generate EAN: "))


barcodes_location = config.barcodes_path_dc2

if not os.path.exists(barcodes_location):
    os.makedirs(barcodes_location)

generate_barcode(Code)

show_image(config.barcodes_path_dc2 + '\\' + Code + ".png", CoordinatesX, CoordinatesY, duration=Timer)

# -25
# 700
# 30
