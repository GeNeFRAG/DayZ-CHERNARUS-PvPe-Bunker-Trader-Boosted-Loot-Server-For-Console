import re
import argparse
import math
from typing import Tuple, List
from pathlib import Path

def parse_coordinates(coord_str: str) -> Tuple[float, float]:
    """
    Parse coordinate string in format x=1346.3, y=9327.0
    
    Args:
        coord_str: String containing coordinates
        
    Returns:
        Tuple of (x, y) coordinates as floats
    """
    try:
        # Extract numbers using regex
        coords = re.findall(r'[xy]=(-?\d+\.?\d*)', coord_str.lower())
        if len(coords) != 2:
            raise ValueError("Invalid coordinate format")
        return float(coords[0]), float(coords[1])
    except Exception as e:
        raise ValueError(f"Failed to parse coordinates: {e}")

def extract_position(line: str) -> Tuple[float, float, float]:
    """
    Extract position coordinates from a log line containing pos=<x, y, z>
    
    Args:
        line: Log line containing position information
        
    Returns:
        Tuple of (x, y, z) coordinates as floats
    """
    try:
        # Extract numbers between < and > using regex
        match = re.search(r'pos=<([-\d.,\s]+)>', line)
        if not match:
            return None
        
        coords = match.group(1).split(',')
        if len(coords) != 3:
            return None
            
        return tuple(float(coord.strip()) for coord in coords)
    except Exception:
        return None

def calculate_distance(x1: float, y1: float, x2: float, y2: float) -> float:
    """
    Calculate 2D distance between two points
    
    Args:
        x1, y1: Coordinates of first point
        x2, y2: Coordinates of second point
        
    Returns:
        Distance in meters
    """
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

def find_nearby_positions(log_file: str, target_x: float, target_y: float, radius: float = 100.0) -> List[str]:
    """
    Find log entries with positions within specified radius
    
    Args:
        log_file: Path to log file
        target_x, target_y: Target coordinates
        radius: Search radius in meters
        
    Returns:
        List of matching log lines
    """
    matching_lines = []
    
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            for line in f:
                pos = extract_position(line)
                if pos:
                    x, y, _ = pos
                    distance = calculate_distance(target_x, target_y, x, y)
                    if distance <= radius:
                        matching_lines.append({
                            'line': line.strip(),
                            'distance': distance,
                            'coords': (x, y)
                        })
    except Exception as e:
        print(f"Error reading log file: {e}")
        return []
        
    return matching_lines

def main():
    parser = argparse.ArgumentParser(description='Find log entries near specified coordinates')
    parser.add_argument('coordinates', help='Coordinates in format "x=1346.3, y=9327.0"')
    parser.add_argument('--log-file', '-f', required=True, help='Path to log file')
    parser.add_argument('--radius', '-r', type=float, default=100.0, 
                       help='Search radius in meters (default: 100)')
    
    args = parser.parse_args()
    
    try:
        # Parse target coordinates
        target_x, target_y = parse_coordinates(args.coordinates)
        print(f"Searching for positions within {args.radius}m of x={target_x}, y={target_y}")
        
        # Find matching positions
        matches = find_nearby_positions(args.log_file, target_x, target_y, args.radius)
        
        # Sort matches by distance
        matches.sort(key=lambda x: x['distance'])
        
        # Print results
        if matches:
            print(f"\nFound {len(matches)} matching entries:")
            for match in matches:
                x, y = match['coords']
                print(f"\nDistance: {match['distance']:.1f}m")
                print(f"Position: <{x}, {y}>")
                print(f"Log entry: {match['line']}")
        else:
            print("\nNo matching positions found")
            
    except ValueError as e:
        print(f"Error: {e}")
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}")
        return 1
        
    return 0

if __name__ == "__main__":
    exit(main())
