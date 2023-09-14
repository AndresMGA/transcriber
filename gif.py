from PIL import Image, ImageDraw

# Set image size and background transparency
width, height = 400, 200
background_color = (0, 0, 0, 0)  # Transparent background

# Create a list of frame durations (in milliseconds)
frame_durations = [500, 1200, 500]
positions = [0, 150, 300]

# Create an empty list to store frames
frames = []

# Create frames with the moving rectangle
for i in range(len(frame_durations)):
    # Create a new transparent image with the specified background for each frame
    frame = Image.new("RGBA", (width, height), background_color)
    draw = ImageDraw.Draw(frame)
    
    # Calculate the position of the rectangle based on the current index
    position = positions[i]
    
    # Draw a red rectangle at the calculated position
    rectangle_color = (255, 0, 0, 255)  # Red color with full opacity
    rectangle_size = (100, 50)  # Rectangle size
    draw.rectangle(((position, 100), (position + rectangle_size[0], 150)), fill=rectangle_color)
    
    # Append the frame to the list of frames
    frames.append(frame)
 
    

# Save the frames as an animated GIF
frames[0].save("moving_rectangle.gif", save_all=True, append_images=frames[1:], duration=frame_durations, loop=0,disposal=2)

print("Animated GIF created.")
