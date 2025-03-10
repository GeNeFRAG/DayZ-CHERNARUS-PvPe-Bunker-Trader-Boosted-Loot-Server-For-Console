import argparse

def is_in_box(x, y, box_ll_x, box_ll_y, box_ur_x, box_ur_y):
    """Check if coordinates are within the specified box."""
    # Handle cases where coordinates might be "reversed"
    min_x = min(box_ll_x, box_ur_x)
    max_x = max(box_ll_x, box_ur_x)
    min_y = min(box_ll_y, box_ur_y)
    max_y = max(box_ll_y, box_ur_y)
    
    return (min_x <= x <= max_x) and (min_y <= y <= max_y)


def extract_coordinates(pos_string):
    """Extract x and y coordinates from a position string."""
    coords = pos_string.split()
    return float(coords[0]), float(coords[2])  # x and z(y) coordinates

def filter_buildings(input_file, output_file, box_ur_x, box_ur_y, box_ll_x, box_ll_y):
    """Filter buildings based on coordinates and write to output file."""
    try:
        with open(input_file, "r") as infile, open(output_file, "w") as outfile:
            for line in infile:
                if 'pos="' in line:
                    # Extract position string
                    pos_start = line.find('pos="') + 5
                    pos_end = line.find('"', pos_start)
                    pos_string = line[pos_start:pos_end]
                    
                    # Get coordinates
                    x, y = extract_coordinates(pos_string)
                    print(f"x: {x}, y: {y}")
                    
                    # Check if coordinates are in box
                    if is_in_box(x, y, box_ll_x, box_ll_y, box_ur_x, box_ur_y):
                        # Write line to output file
                        print(f"Writing line to output file: {line}")
                        outfile.write(line)
        print(f"Filtered buildings have been saved to {output_file}")
        return True
    except FileNotFoundError:
        print(f"Error: Could not find input file {input_file}")
        return False
    except Exception as e:
        print(f"Error: An unexpected error occurred: {str(e)}")
        return False

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Filter buildings within specified coordinate box.')
    
    parser.add_argument('--input', '-i',
                        default='mapgrouppos.xml',
                        help='Input XML file (default: mapgrouppos.xml)')
    
    parser.add_argument('--output', '-o',
                        default='buildings_in_box.xml',
                        help='Output XML file (default: buildings_in_box.xml)')
    
    parser.add_argument('--ur-x', '-ux',
                        type=float,
                        required=True,
                        help='Upper right X coordinate')
    
    parser.add_argument('--ur-y', '-uy',
                        type=float,
                        required=True,
                        help='Upper right Y coordinate')
    
    parser.add_argument('--ll-x', '-lx',
                        type=float,
                        required=True,
                        help='Lower left X coordinate')
    
    parser.add_argument('--ll-y', '-ly',
                        type=float,
                        required=True,
                        help='Lower left Y coordinate')
    
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()
    
    # Run the filter with provided arguments
    filter_buildings(
        input_file=args.input,
        output_file=args.output,
        box_ur_x=args.ur_x,
        box_ur_y=args.ur_y,
        box_ll_x=args.ll_x,
        box_ll_y=args.ll_y
    )
