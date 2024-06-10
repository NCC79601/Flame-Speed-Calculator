import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import numpy as np
from colorama import Fore, Style

class FlameSpeedCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("Flame Speed Calculator")
        self.points = []  # List to store the points
        self.target_width = 900  # Modify target width
        self.target_height = 600
        self.image_loaded = False  # Flag to check if an image is loaded
        
        self.canvas = tk.Canvas(root, cursor="cross", width=self.target_width, height=self.target_height)
        self.canvas.pack()
        
        self.button_frame = tk.Frame(root)
        self.button_frame.pack(pady=10)  # Add vertical padding around the frame
        
        self.load_button = tk.Button(self.button_frame, text="Load Image", command=self.load_image)
        self.load_button.pack(side=tk.LEFT, padx=5, pady=5)  # Add padding around the button
        
        self.clear_button = tk.Button(self.button_frame, text="Clear Points", command=self.clear_points)
        self.clear_button.pack(side=tk.LEFT, padx=5, pady=5)  # Add padding around the button
        
        self.canvas.bind("<Button-1>", self.mark_point)
        
        # Add entries for Methane, Air, and Ammonia flow rates
        self.entry_frame = tk.Frame(root)
        self.entry_frame.pack(pady=10)  # Add vertical padding around the frame
        
        tk.Label(self.entry_frame, text="CH4 (L/min):").pack(side=tk.LEFT)
        self.methane_entry = tk.Entry(self.entry_frame)
        self.methane_entry.pack(side=tk.LEFT, padx=10)
        
        tk.Label(self.entry_frame, text="Air (L/min):").pack(side=tk.LEFT)
        self.air_entry = tk.Entry(self.entry_frame)
        self.air_entry.pack(side=tk.LEFT, padx=10)
        
        tk.Label(self.entry_frame, text="NH3 (L/min):").pack(side=tk.LEFT)
        self.ammonia_entry = tk.Entry(self.entry_frame)
        self.ammonia_entry.pack(side=tk.LEFT, padx=10)
        
        # Add calculate button
        self.calculate_button = tk.Button(root, text="Calculate", bg="green", fg="white", command=self.calculate)
        self.calculate_button.pack(pady=10)  # Add vertical padding around the button
    
    def load_image(self):
        file_path = filedialog.askopenfilename()
        if not file_path:
            print("Invalid file path.")
            return
        
        self.image = Image.open(file_path)
        
        # Calculate the scale to maintain aspect ratio
        self.scale = min(self.target_width / self.image.width, self.target_height / self.image.height)
        new_size = (int(self.image.width * self.scale), int(self.image.height * self.scale))
        self.image = self.image.resize(new_size, Image.Resampling.LANCZOS)
        
        self.tk_image = ImageTk.PhotoImage(self.image)
        self.canvas.config(width=self.target_width, height=self.target_height)
        self.canvas.create_image((self.target_width - new_size[0]) // 2, (self.target_height - new_size[1]) // 2, anchor=tk.NW, image=self.tk_image)
        
        self.clear_points()  # Clear points when a new image is loaded
        self.image_loaded = True  # Set the flag to True indicating an image is loaded
        
    def mark_point(self, event):
        if not self.image_loaded:
            print("No image loaded. Please load an image first.")
            return

        if len(self.points) < 3:
            x, y = event.x, event.y
            colors = ['red', 'green', 'blue']
            color = colors[len(self.points)]
            
            self.points.append((x, y))
            self.canvas.create_oval(x-5, y-5, x+5, y+5, outline=color, width=2, fill=color)
            print(f"Point {len(self.points)}: ({x}, {y})")

            if len(self.points) == 3:
                # Draw lines when all three points are available
                self.canvas.create_line(self.points[0], self.points[2], fill='cyan', width=2)
                self.canvas.create_line(self.points[1], self.points[2], fill='cyan', width=2)
                self.canvas.create_line(self.points[0], self.points[1], fill='yellow', width=2)

                (x1, y1), (x2, y2), (x3, y3) = [(x, y) for x, y in self.points]
                v1 = np.array([x2 - x1, y2 - y1]) # vertical
                v2 = np.array([x3 - x1, y3 - y1]) # diagonal-left
                v3 = np.array([x3 - x2, y3 - y2]) # diagonal-right
                scale_coeff = 19.5 / np.linalg.norm(v1) # Scale coefficient from pic to real (mm)

                semi_apex_angle = 0.5 * np.arccos(np.dot(v2, v3) / (np.linalg.norm(v2) * np.linalg.norm(v3))) # semi apex angle in radians
                semi_apex_angle_deg = np.rad2deg(semi_apex_angle) # convert to degrees

                v_vert = v2 - np.dot(v1, v2) / np.dot(v1, v1) * v1

                flame_height = np.linalg.norm(v_vert) * scale_coeff

                print(f'Semi apex angle: {semi_apex_angle_deg} degrees')
                print(Fore.YELLOW + f'Flame height:    {flame_height} mm' + Style.RESET_ALL)

                self.semi_apex_angle = semi_apex_angle_deg
                self.flame_height    = flame_height
    
    def clear_points(self):
        self.points = []
        self.canvas.delete("all")
        if self.image_loaded:
            self.canvas.create_image((self.target_width - self.tk_image.width()) // 2, 
                                     (self.target_height - self.tk_image.height()) // 2, 
                                     anchor=tk.NW, image=self.tk_image)
    
    def calculate(self):
        if len(self.points) != 3:
            print("Please mark three points on the image.")
            return
        
        try:
            methane_flow = float(self.methane_entry.get())
            air_flow = float(self.air_entry.get())
            ammonia_flow = float(self.ammonia_entry.get())
        except ValueError:
            print("Please enter valid flow rates.")
            return

        # Placeholder function
        self.perform_calculation(self.points, methane_flow, air_flow, ammonia_flow)
    
    def perform_calculation(self, points, methane_flow, air_flow, ammonia_flow):
        print(f"CH4: {methane_flow} L/min")
        print(f"Air: {air_flow} L/min")
        print(f"NH3: {ammonia_flow} L/min")

        # equivalence ratio
        A_to_F_stoic = 9.52
        A_to_F = air_flow / methane_flow
        phi = A_to_F / A_to_F_stoic
        print(f'Equivalence ratio: {phi}')

        # NH3 ratio
        NH3_ratio = ammonia_flow / (methane_flow + ammonia_flow)
        print(f'NH3 ratio: {100*NH3_ratio:.2f}%')

        total_flow = methane_flow + air_flow + ammonia_flow # L/min
        total_flow = total_flow
        v_u = total_flow * 1e-3 / 60 / (np.pi * (14.3e-3 / 2)**2)
        print(f'Unburned velocity: {v_u} m/s')
        
        # laminar flame speed
        S_L = v_u * np.sin(np.deg2rad(self.semi_apex_angle))
        print(Fore.YELLOW + f'Flame velocity: S_L = {S_L} m/s' + Style.RESET_ALL)


if __name__ == "__main__":
    root = tk.Tk()
    app = FlameSpeedCalculator(root)
    root.mainloop()
