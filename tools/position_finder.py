import re
import math
from typing import List, Tuple, Optional
import glob
import os
from datetime import datetime
import csv

def extract_info(line: str, file_date: str) -> Tuple[Optional[str], Optional[str], Optional[tuple], Optional[str]]:
    """
    Extract time, player name, position coordinates, and action from a line of text
    
    Args:
        line: String containing player data
        file_date: Date extracted from filename
        
    Returns:
        Tuple of (time_str, player_name, (x, y, z) coordinates, action)
    """
    try:
        # Split the line by '|' to get the time
        parts = line.split('|', 1)
        time_str = parts[0].strip() if len(parts) > 0 else None

        # Extract player name
        name_match = re.search(r'"([^"]+)"', line)
        player_name = name_match.group(1) if name_match else None

        # Extract position
        pos_match = re.search(r'pos=<([-\d.,\s]+)>', line)
        if not pos_match:
            # Try CSV format
            parts = line.split(',')
            if len(parts) >= 9:  # Assuming CSV format with at least 9 columns
                try:
                    x = float(parts[5])
                    y = float(parts[6])
                    z = float(parts[7])
                    time_str = parts[3]
                    player_name = parts[4]
                    action = parts[8]
                    return time_str, player_name, (x, y, z), action
                except (ValueError, IndexError):
                    pass
            return time_str, player_name, None, None
        
        coords = pos_match.group(1).split(',')
        if len(coords) != 3:
            return time_str, player_name, None, None
            
        position = tuple(float(coord.strip()) for coord in coords)
        
        # Extract action (everything after the coordinates)
        action_match = re.search(r'>\s*(.*?)(?:\s*\(|$)', line)
        action = action_match.group(1).strip() if action_match else ""
        
        return time_str, player_name, position, action
    except Exception as e:
        print(f"Error extracting info: {e}")
        return None, None, None, None

def extract_date_from_filename(filename: str) -> str:
    """
    Extract date from filename format DayZServer_X1_x64_2025_03_03_160233687.ADM
    """
    try:
        # Extract date components from filename
        date_match = re.search(r'_(\d{4})_(\d{2})_(\d{2})_', filename)
        if date_match:
            year, month, day = date_match.groups()
            return f"{year}-{month}-{day}"
    except Exception as e:
        print(f"Error extracting date from filename: {e}")
    return "Unknown date"

def calculate_distance(x1: float, y1: float, x2: float, y2: float) -> float:
    """
    Calculate 2D distance between two points
    """
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

def find_nearby_positions(file_pattern: str, target_x: float, target_y: float, radius: float = 100.0) -> List[tuple]:
    """
    Find positions within specified radius of target coordinates in multiple files
    """
    nearby_positions = []
    
    matching_files = glob.glob(file_pattern)
    
    for file_path in matching_files:
        try:
            file_date = extract_date_from_filename(os.path.basename(file_path))
            
            with open(file_path, 'r', encoding='utf-8') as file:
                for line_num, line in enumerate(file, 1):
                    time_str, player_name, coords, action = extract_info(line, file_date)
                    
                    if coords:
                        x, y, z = coords
                        distance = calculate_distance(target_x, target_y, x, y)
                        
                        if distance <= radius:
                            nearby_positions.append((
                                os.path.basename(file_path),
                                line_num,
                                file_date,
                                time_str,
                                player_name,
                                coords,
                                action,
                                distance
                            ))
        except Exception as e:
            print(f"Error processing file {file_path}: {str(e)}")
            
    return sorted(nearby_positions, key=lambda x: x[7])  # Sort by distance

def save_to_csv(results: List[tuple], output_file: str):
    """
    Save results to CSV file
    
    Args:
        results: List of result tuples
        output_file: Name of the CSV file to create
    """
    headers = ['File', 'Line', 'Date', 'Time', 'Player', 'X', 'Y', 'Z', 'Action', 'Distance']
    
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)
        
        for filename, line_num, file_date, time_str, player_name, coords, action, distance in results:
            writer.writerow([
                filename,
                line_num,
                file_date,
                time_str,
                player_name,
                f"{coords[0]:.1f}",
                f"{coords[1]:.1f}",
                f"{coords[2]:.1f}",
                action if action else "",
                f"{distance:.2f}"
            ])

def save_to_csv(results: List[tuple], output_file: str):
    """
    Save results to CSV file
    
    Args:
        results: List of result tuples
        output_file: Name of the CSV file to create
    """
    headers = ['File', 'Line', 'Date', 'Time', 'Player', 'X', 'Y', 'Z', 'Action', 'Distance']
    
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)
        
        for filename, line_num, file_date, time_str, player_name, coords, action, distance in results:
            writer.writerow([
                filename,
                line_num,
                file_date,
                time_str,
                player_name,
                f"{coords[0]:.1f}",
                f"{coords[1]:.1f}",
                f"{coords[2]:.1f}",
                action if action else "",
                f"{distance:.2f}"
            ])

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Find nearby player positions and actions in files')
    parser.add_argument('file_pattern', help='File pattern to search (e.g. "*.ADM")')
    parser.add_argument('target_x', type=float, help='Target X coordinate')
    parser.add_argument('target_y', type=float, help='Target Y coordinate')
    parser.add_argument('--radius', type=float, default=100.0, help='Search radius in meters')
    parser.add_argument('--output', default='results.csv', help='Output CSV file name (default: results.csv)')
    
    args = parser.parse_args()
    
    results = find_nearby_positions(args.file_pattern, args.target_x, args.target_y, args.radius)
    
    if not results:
        print("No positions found within specified radius.")
        return
    
    # Save to CSV
    save_to_csv(results, args.output)
    
    print(f"\nFound {len(results)} positions within {args.radius}m radius.")
    print(f"Results have been saved to: {args.output}")

if __name__ == "__main__":
    main()

