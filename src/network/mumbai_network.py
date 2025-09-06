"""
Mumbai Railway Network Structure
Defines the core railway network topology for the Mumbai Suburban Railway system.
"""

from enum import Enum
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
import networkx as nx


class LineType(Enum):
    """Railway line types in Mumbai suburban network"""
    WESTERN = "western"
    CENTRAL_MAIN = "central_main"
    CENTRAL_HARBOUR = "central_harbour"
    TRANS_HARBOUR = "trans_harbour"


class StationType(Enum):
    """Types of railway stations"""
    TERMINAL = "terminal"
    JUNCTION = "junction"
    REGULAR = "regular"
    HALT = "halt"


@dataclass
class Station:
    """Represents a railway station in the Mumbai network"""
    id: str
    name: str
    line: LineType
    station_type: StationType
    coordinates: Tuple[float, float]  # (latitude, longitude)
    platforms: int = 2
    capacity: int = 1000  # passenger capacity
    interchange: bool = False
    interchange_lines: List[LineType] = None
    
    def __post_init__(self):
        if self.interchange_lines is None:
            self.interchange_lines = []


@dataclass
class Track:
    """Represents a track segment between two stations"""
    id: str
    from_station: str
    to_station: str
    line: LineType
    distance_km: float
    travel_time_minutes: float
    capacity: int = 2  # number of trains that can be on this track
    bidirectional: bool = True
    signal_blocks: int = 1  # number of signal blocks on this track


class MumbaiRailwayNetwork:
    """
    Main class representing the Mumbai Suburban Railway network topology
    """
    
    def __init__(self):
        self.stations: Dict[str, Station] = {}
        self.tracks: Dict[str, Track] = {}
        self.network_graph = nx.MultiDiGraph()
        self._initialize_network()
    
    def _initialize_network(self):
        """Initialize the Mumbai railway network with actual station data"""
        self._create_western_line()
        self._create_central_main_line()
        self._create_central_harbour_line()
        self._create_trans_harbour_line()
        self._create_interchange_connections()
    
    def _create_western_line(self):
        """Create Western Railway line stations and tracks"""
        western_stations = [
            # Main Western Line stations (sample - you can expand)
            ("CST", "Chhatrapati Shivaji Terminus", StationType.TERMINAL, (18.9398, 72.8355), 18),
            ("CCG", "Churchgate", StationType.TERMINAL, (18.9322, 72.8264), 12),
            ("MRN", "Marine Lines", StationType.REGULAR, (18.9434, 72.8234), 4),
            ("CRL", "Charni Road", StationType.REGULAR, (18.9514, 72.8199), 4),
            ("GTR", "Grant Road", StationType.REGULAR, (18.9629, 72.8181), 4),
            ("BCT", "Mumbai Central", StationType.JUNCTION, (18.9685, 72.8205), 8),
            ("MSR", "Masjid Bunder", StationType.REGULAR, (18.9741, 72.8311), 4),
            ("SXD", "Sandhurst Road", StationType.REGULAR, (18.9852, 72.8372), 4),
            ("BYC", "Byculla", StationType.REGULAR, (18.9793, 72.8328), 4),
            ("DAD", "Dadar", StationType.JUNCTION, (19.0188, 72.8437), 8),
            ("MTN", "Matunga", StationType.REGULAR, (19.0270, 72.8567), 4),
            ("MHM", "Mahim", StationType.REGULAR, (19.0410, 72.8416), 4),
            ("BVI", "Bandra", StationType.JUNCTION, (19.0544, 72.8407), 6),
            ("ADH", "Andheri", StationType.JUNCTION, (19.1197, 72.8464), 8),
            ("BOR", "Borivali", StationType.JUNCTION, (19.2307, 72.8567), 6),
            ("VR", "Virar", StationType.TERMINAL, (19.4559, 72.8081), 4),
        ]
        
        for station_data in western_stations:
            station = Station(
                id=station_data[0],
                name=station_data[1],
                line=LineType.WESTERN,
                station_type=station_data[2],
                coordinates=station_data[3],
                platforms=station_data[4]
            )
            self.stations[station.id] = station
            self.network_graph.add_node(station.id, **station.__dict__)
        
        # Create tracks between consecutive stations
        self._create_consecutive_tracks(western_stations, LineType.WESTERN)
    
    def _create_central_main_line(self):
        """Create Central Railway main line stations and tracks"""
        central_main_stations = [
            ("CST", "Chhatrapati Shivaji Terminus", StationType.TERMINAL, (18.9398, 72.8355), 18),
            ("BYC", "Byculla", StationType.REGULAR, (18.9793, 72.8328), 4),
            ("DAD", "Dadar", StationType.JUNCTION, (19.0188, 72.8437), 8),
            ("KRL", "Kurla", StationType.JUNCTION, (19.0728, 72.8794), 6),
            ("GHY", "Ghatkopar", StationType.REGULAR, (19.0864, 72.9081), 4),
            ("VKD", "Vikhroli", StationType.REGULAR, (19.1053, 72.9294), 4),
            ("TNA", "Thane", StationType.JUNCTION, (19.1972, 72.9568), 8),
            ("KYN", "Kalyan", StationType.JUNCTION, (19.2437, 73.1355), 8),
            ("KJT", "Karjat", StationType.TERMINAL, (18.9107, 73.3206), 4),
        ]
        
        for station_data in central_main_stations:
            station_id = station_data[0]
            if station_id not in self.stations:  # Avoid duplicates for interchange stations
                station = Station(
                    id=station_data[0],
                    name=station_data[1],
                    line=LineType.CENTRAL_MAIN,
                    station_type=station_data[2],
                    coordinates=station_data[3],
                    platforms=station_data[4]
                )
                self.stations[station.id] = station
                self.network_graph.add_node(station.id, **station.__dict__)
        
        self._create_consecutive_tracks(central_main_stations, LineType.CENTRAL_MAIN)
    
    def _create_central_harbour_line(self):
        """Create Central Railway harbour line stations and tracks"""
        harbour_stations = [
            ("CST", "Chhatrapati Shivaji Terminus", StationType.TERMINAL, (18.9398, 72.8355), 18),
            ("KRD", "King's Circle", StationType.REGULAR, (19.0375, 72.8615), 2),
            ("KRL", "Kurla", StationType.JUNCTION, (19.0728, 72.8794), 6),
            ("CHT", "Chembur", StationType.REGULAR, (19.0622, 72.8972), 2),
            ("PNV", "Panvel", StationType.TERMINAL, (18.9894, 73.1175), 4),
        ]
        
        # Add only new stations (avoid duplicates)
        for station_data in harbour_stations:
            station_id = station_data[0]
            if station_id not in self.stations:
                station = Station(
                    id=station_data[0],
                    name=station_data[1],
                    line=LineType.CENTRAL_HARBOUR,
                    station_type=station_data[2],
                    coordinates=station_data[3],
                    platforms=station_data[4]
                )
                self.stations[station.id] = station
                self.network_graph.add_node(station.id, **station.__dict__)
        
        self._create_consecutive_tracks(harbour_stations, LineType.CENTRAL_HARBOUR)
    
    def _create_trans_harbour_line(self):
        """Create Trans-Harbour line stations and tracks"""
        trans_harbour_stations = [
            ("TNA", "Thane", StationType.JUNCTION, (19.1972, 72.9568), 8),
            ("VAS", "Vashi", StationType.JUNCTION, (19.0770, 73.0169), 4),
            ("PNV", "Panvel", StationType.TERMINAL, (18.9894, 73.1175), 4),
        ]
        
        # Add only new stations
        for station_data in trans_harbour_stations:
            station_id = station_data[0]
            if station_id not in self.stations:
                station = Station(
                    id=station_data[0],
                    name=station_data[1],
                    line=LineType.TRANS_HARBOUR,
                    station_type=station_data[2],
                    coordinates=station_data[3],
                    platforms=station_data[4]
                )
                self.stations[station.id] = station
                self.network_graph.add_node(station.id, **station.__dict__)
        
        self._create_consecutive_tracks(trans_harbour_stations, LineType.TRANS_HARBOUR)
    
    def _create_consecutive_tracks(self, stations_list, line_type):
        """Create tracks between consecutive stations"""
        for i in range(len(stations_list) - 1):
            from_station = stations_list[i][0]
            to_station = stations_list[i + 1][0]
            
            # Calculate approximate distance and travel time
            from_coords = stations_list[i][3]
            to_coords = stations_list[i + 1][3]
            distance = self._calculate_distance(from_coords, to_coords)
            travel_time = self._estimate_travel_time(distance)
            
            track_id = f"{from_station}_{to_station}_{line_type.value}"
            track = Track(
                id=track_id,
                from_station=from_station,
                to_station=to_station,
                line=line_type,
                distance_km=distance,
                travel_time_minutes=travel_time
            )
            
            self.tracks[track_id] = track
            self.network_graph.add_edge(
                from_station, 
                to_station, 
                key=line_type.value,
                **track.__dict__
            )
    
    def _create_interchange_connections(self):
        """Create interchange connections between different lines"""
        # Mark interchange stations
        interchanges = {
            "CST": [LineType.WESTERN, LineType.CENTRAL_MAIN, LineType.CENTRAL_HARBOUR],
            "DAD": [LineType.WESTERN, LineType.CENTRAL_MAIN],
            "BYC": [LineType.WESTERN, LineType.CENTRAL_MAIN],
            "KRL": [LineType.CENTRAL_MAIN, LineType.CENTRAL_HARBOUR],
            "TNA": [LineType.CENTRAL_MAIN, LineType.TRANS_HARBOUR],
            "PNV": [LineType.CENTRAL_HARBOUR, LineType.TRANS_HARBOUR],
        }
        
        for station_id, lines in interchanges.items():
            if station_id in self.stations:
                self.stations[station_id].interchange = True
                self.stations[station_id].interchange_lines = lines
    
    def _calculate_distance(self, coord1: Tuple[float, float], coord2: Tuple[float, float]) -> float:
        """Calculate approximate distance between two coordinates in km"""
        import math
        
        lat1, lon1 = coord1
        lat2, lon2 = coord2
        
        # Haversine formula for approximate distance
        R = 6371  # Earth's radius in km
        dLat = math.radians(lat2 - lat1)
        dLon = math.radians(lon2 - lon1)
        
        a = (math.sin(dLat/2) * math.sin(dLat/2) + 
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * 
             math.sin(dLon/2) * math.sin(dLon/2))
        
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        distance = R * c
        
        return round(distance, 2)
    
    def _estimate_travel_time(self, distance_km: float) -> float:
        """Estimate travel time between stations based on distance"""
        # Average speed in Mumbai suburban trains: ~25-30 km/h including stops
        average_speed = 27  # km/h
        base_time = (distance_km / average_speed) * 60  # minutes
        
        # Add station stop time
        stop_time = 1.5  # minutes per station
        
        return round(base_time + stop_time, 1)
    
    def get_station(self, station_id: str) -> Optional[Station]:
        """Get station by ID"""
        return self.stations.get(station_id)
    
    def get_stations_by_line(self, line: LineType) -> List[Station]:
        """Get all stations on a specific line"""
        return [station for station in self.stations.values() 
                if line in station.interchange_lines or station.line == line]
    
    def get_route(self, from_station: str, to_station: str) -> Optional[List[str]]:
        """Find shortest route between two stations"""
        try:
            return nx.shortest_path(self.network_graph, from_station, to_station)
        except nx.NetworkXNoPath:
            return None
    
    def get_network_stats(self) -> Dict:
        """Get basic network statistics"""
        return {
            "total_stations": len(self.stations),
            "total_tracks": len(self.tracks),
            "interchange_stations": len([s for s in self.stations.values() if s.interchange]),
            "lines": len(LineType),
            "network_diameter": nx.diameter(self.network_graph.to_undirected()) if self.network_graph.number_of_nodes() > 0 else 0
        }
