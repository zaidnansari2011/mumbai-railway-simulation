#!/usr/bin/env python3
"""
Script to display Mumbai Railway Network statistics
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.network.mumbai_network import MumbaiRailwayNetwork, LineType

def main():
    # Create network
    network = MumbaiRailwayNetwork()
    stats = network.get_network_stats()
    
    print('=== MUMBAI RAILWAY NETWORK STATISTICS ===')
    print(f'Total Stations: {stats["total_stations"]}')
    print(f'Total Tracks: {stats["total_tracks"]}')
    print(f'Interchange Stations: {stats["interchange_stations"]}')
    print(f'Number of Lines: {stats["lines"]}')
    print()
    
    # Count platforms by line
    total_platforms = 0
    print('=== STATIONS BY LINE ===')
    for line in LineType:
        stations = network.get_stations_by_line(line)
        line_platforms = sum(station.platforms for station in stations)
        total_platforms += line_platforms
        print(f'{line.value.title()} Line: {len(stations)} stations, {line_platforms} platforms')
    
    print()
    print(f'Total Platforms across all lines: {total_platforms}')
    print()
    
    print('=== DETAILED STATION LIST ===')
    print('Station ID | Station Name                    | Platforms | Line          | Interchange')
    print('-----------|--------------------------------|-----------|---------------|------------')
    
    for station_id, station in sorted(network.stations.items()):
        interchange_info = 'Yes' if station.interchange else 'No'
        line_name = station.line.value.title() if hasattr(station, 'line') else 'Multiple'
        print(f'{station_id:10} | {station.name:30} | {station.platforms:8} | {line_name:13} | {interchange_info}')
    
    print()
    print('=== INTERCHANGE STATIONS DETAILS ===')
    for station_id, station in network.stations.items():
        if station.interchange:
            lines = [line.value for line in station.interchange_lines]
            print(f'{station.name} ({station_id}): {", ".join(lines)} - {station.platforms} platforms')

if __name__ == "__main__":
    main()
