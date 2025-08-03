import numpy as np
from scipy.ndimage import distance_transform_edt, label, binary_dilation, binary_erosion
from skimage.graph import route_through_array
from skimage.morphology import skeletonize
import heapq

GLOBAL_MIN_DEPTH = -3.0
MAX_BRIDGE_GAP = 100
MIN_STRAIT_WIDTH = 2

MAJOR_WATERWAYS = [
    {
        'name': 'Panama Canal',
        'path': [
            (9.6, -79.9), (9.5, -79.8), (9.4, -79.7), (9.3, -79.6), 
            (9.2, -79.5), (9.1, -79.4), (9.0, -79.3), (8.9, -79.2)
        ],
        'width_km': 5
    },
    {
        'name': 'Suez Canal',
        'path': [
            (31.6, 32.3), (31.4, 32.3), (31.2, 32.3), (31.0, 32.3),
            (30.8, 32.3), (30.6, 32.3), (30.4, 32.3), (30.2, 32.3),
            (30.0, 32.3), (29.8, 32.3), (29.6, 32.3), (29.4, 32.3),
            (29.2, 32.3), (29.0, 32.3), (28.8, 32.3), (28.6, 32.3)
        ],
        'width_km': 3
    },
    {
        'name': 'Strait of Gibraltar',
        'path': [
            (36.2, -5.8), (36.1, -5.7), (36.0, -5.6), (35.9, -5.5), (35.8, -5.4)
        ],
        'width_km': 14
    },
    {
        'name': 'Bosphorus Strait',
        'path': [
            (41.3, 29.0), (41.2, 29.0), (41.1, 29.1), (41.0, 29.1), (40.9, 29.1)
        ],
        'width_km': 2
    },
    {
        'name': 'Dardanelles Strait',
        'path': [
            (40.4, 26.4), (40.3, 26.5), (40.2, 26.6), (40.1, 26.7), (40.0, 26.8)
        ],
        'width_km': 3
    },
    {
        'name': 'English Channel',
        'path': [
            (51.1, 1.4), (50.9, 1.2), (50.7, 1.0), (50.5, 0.8), 
            (50.3, 0.6), (50.1, 0.4), (49.9, 0.2), (49.7, 0.0)
        ],
        'width_km': 20
    },
    {
        'name': 'Strait of Hormuz',
        'path': [
            (26.6, 56.2), (26.5, 56.3), (26.4, 56.4), (26.3, 56.5), (26.2, 56.6)
        ],
        'width_km': 33
    },
    {
        'name': 'Strait of Malacca',
        'path': [
            (5.8, 95.3), (5.5, 96.0), (5.2, 96.7), (4.9, 97.4), 
            (4.6, 98.1), (4.3, 98.8), (4.0, 99.5), (3.7, 100.2),
            (3.4, 100.9), (3.1, 101.6), (2.8, 102.3), (2.5, 103.0),
            (2.2, 103.7), (1.9, 104.4), (1.6, 105.1)
        ],
        'width_km': 2.8
    },
    {
        'name': 'Strait of Dover',
        'path': [
            (51.1, 1.4), (50.9, 1.2), (50.7, 1.0)
        ],
        'width_km': 34
    },
    {
        'name': 'Cook Strait',
        'path': [
            (-41.1, 174.8), (-41.2, 174.9), (-41.3, 175.0), (-41.4, 175.1)
        ],
        'width_km': 23
    },
    {
        'name': 'Bass Strait',
        'path': [
            (-40.5, 144.0), (-40.3, 145.0), (-40.1, 146.0), 
            (-39.9, 147.0), (-39.7, 148.0), (-39.5, 149.0)
        ],
        'width_km': 240
    },
    {
        'name': 'Torres Strait',
        'path': [
            (-10.1, 142.2), (-10.0, 142.4), (-9.9, 142.6), (-9.8, 142.8)
        ],
        'width_km': 150
    },
    {
        'name': 'Denmark Strait',
        'path': [
            (67.0, -27.0), (66.5, -26.0), (66.0, -25.0), (65.5, -24.0)
        ],
        'width_km': 290
    },
    {
        'name': 'Drake Passage',
        'path': [
            (-55.8, -67.3), (-56.0, -66.0), (-56.2, -64.7), (-56.4, -63.4)
        ],
        'width_km': 800
    },
    {
        'name': 'Bering Strait',
        'path': [
            (65.8, -169.0), (65.9, -168.5), (66.0, -168.0), (66.1, -167.5)
        ],
        'width_km': 85
    },
    {
        'name': 'Tsugaru Strait',
        'path': [
            (41.5, 140.0), (41.4, 140.5), (41.3, 141.0), (41.2, 141.5)
        ],
        'width_km': 19
    },
    {
        'name': 'Taiwan Strait',
        'path': [
            (25.5, 119.5), (25.0, 119.7), (24.5, 119.9), (24.0, 120.1),
            (23.5, 120.3), (23.0, 120.5)
        ],
        'width_km': 180
    },
    {
        'name': 'Luzon Strait',
        'path': [
            (21.5, 121.0), (21.0, 121.2), (20.5, 121.4), (20.0, 121.6)
        ],
        'width_km': 340
    },
    {
        'name': 'Korean Strait',
        'path': [
            (34.5, 129.0), (34.3, 129.2), (34.1, 129.4), (33.9, 129.6)
        ],
        'width_km': 200
    },
    {
        'name': 'Mozambique Channel',
        'path': [
            (-11.0, 40.5), (-12.0, 41.0), (-13.0, 41.5), (-14.0, 42.0),
            (-15.0, 42.5), (-16.0, 43.0), (-17.0, 43.5), (-18.0, 44.0),
            (-19.0, 44.5), (-20.0, 45.0), (-21.0, 45.5), (-22.0, 46.0),
            (-23.0, 46.5), (-24.0, 47.0), (-25.0, 47.5)
        ],
        'width_km': 460
    },
    {
        'name': 'Yucatan Channel',
        'path': [
            (21.8, -84.8), (21.6, -85.2), (21.4, -85.6), (21.2, -86.0)
        ],
        'width_km': 217
    },
    {
        'name': 'Florida Straits',
        'path': [
            (25.8, -80.1), (25.5, -80.5), (25.2, -80.9), (24.9, -81.3),
            (24.6, -81.7), (24.3, -82.1)
        ],
        'width_km': 150
    },
    {
        'name': 'Windward Passage',
        'path': [
            (20.1, -73.8), (20.0, -73.9), (19.9, -74.0), (19.8, -74.1)
        ],
        'width_km': 80
    },
    {
        'name': 'Mona Passage',
        'path': [
            (18.5, -67.9), (18.4, -68.0), (18.3, -68.1), (18.2, -68.2)
        ],
        'width_km': 130
    },
    {
        'name': 'Cabot Strait',
        'path': [
            (47.1, -59.7), (47.0, -59.9), (46.9, -60.1), (46.8, -60.3)
        ],
        'width_km': 104
    },
    {
        'name': 'Belle Isle Strait',
        'path': [
            (51.8, -55.4), (51.7, -55.6), (51.6, -55.8), (51.5, -56.0)
        ],
        'width_km': 17
    },
    {
        'name': 'Great Belt',
        'path': [
            (55.3, 10.9), (55.2, 11.0), (55.1, 11.1), (55.0, 11.2)
        ],
        'width_km': 18
    },
    {
        'name': 'Little Belt',
        'path': [
            (55.5, 9.7), (55.4, 9.8), (55.3, 9.9), (55.2, 10.0)
        ],
        'width_km': 0.8
    },
    {
        'name': 'The Sound (Oresund)',
        'path': [
            (56.1, 12.6), (56.0, 12.7), (55.9, 12.8), (55.8, 12.9)
        ],
        'width_km': 4
    },
    {
        'name': 'Skagerrak',
        'path': [
            (58.0, 8.0), (57.8, 8.5), (57.6, 9.0), (57.4, 9.5),
            (57.2, 10.0), (57.0, 10.5), (56.8, 11.0)
        ],
        'width_km': 240
    },
    {
        'name': 'Kattegat',
        'path': [
            (57.7, 11.5), (57.5, 11.7), (57.3, 11.9), (57.1, 12.1),
            (56.9, 12.3), (56.7, 12.5)
        ],
        'width_km': 60
    },
    {
        'name': 'Strait of Bonifacio',
        'path': [
            (41.4, 9.0), (41.3, 9.1), (41.2, 9.2), (41.1, 9.3)
        ],
        'width_km': 11
    },
    {
        'name': 'Strait of Messina',
        'path': [
            (38.2, 15.6), (38.1, 15.7), (38.0, 15.8), (37.9, 15.9)
        ],
        'width_km': 3
    },
    {
        'name': 'Strait of Otranto',
        'path': [
            (40.1, 18.5), (40.0, 18.7), (39.9, 18.9), (39.8, 19.1)
        ],
        'width_km': 72
    },
    {
        'name': 'Kerch Strait',
        'path': [
            (45.4, 36.5), (45.3, 36.6), (45.2, 36.7), (45.1, 36.8)
        ],
        'width_km': 4.5
    },
    {
        'name': 'Strait of Canso',
        'path': [
            (45.6, -61.4), (45.5, -61.5), (45.4, -61.6)
        ],
        'width_km': 1.4
    },
    {
        'name': 'Strait of Juan de Fuca',
        'path': [
            (48.5, -124.8), (48.4, -124.0), (48.3, -123.2), (48.2, -122.4)
        ],
        'width_km': 20
    },
    {
        'name': 'Puget Sound',
        'path': [
            (47.6, -122.3), (47.4, -122.5), (47.2, -122.7), (47.0, -122.9)
        ],
        'width_km': 3
    }
]

def coord_to_grid_index(lat, lon, grid_lat, grid_lon):
    lat_idx = np.abs(grid_lat - lat).argmin()
    lon_idx = np.abs(grid_lon - lon).argmin()
    return int(lat_idx), int(lon_idx)

def add_waterway_passages(cost_grid, lat_grid, lon_grid):
    waterways_added = 0
    
    for waterway in MAJOR_WATERWAYS:
        waterway_path = waterway['path']
        width_km = waterway['width_km']
        
        lat_resolution = abs(lat_grid[1] - lat_grid[0]) if len(lat_grid) > 1 else 0.1
        lon_resolution = abs(lon_grid[1] - lon_grid[0]) if len(lon_grid) > 1 else 0.1
        
        width_cells_lat = max(1, int(width_km * 0.01 / lat_resolution))
        width_cells_lon = max(1, int(width_km * 0.01 / lon_resolution))
        
        path_in_bounds = []
        for lat, lon in waterway_path:
            if (lat_grid.min() <= lat <= lat_grid.max() and 
                lon_grid.min() <= lon <= lon_grid.max()):
                path_in_bounds.append((lat, lon))
        
        if len(path_in_bounds) < 2:
            continue
        
        for i in range(len(path_in_bounds) - 1):
            lat1, lon1 = path_in_bounds[i]
            lat2, lon2 = path_in_bounds[i + 1]
            
            steps = max(10, int(np.sqrt((lat2-lat1)**2 + (lon2-lon1)**2) / min(lat_resolution, lon_resolution)))
            lats = np.linspace(lat1, lat2, steps)
            lons = np.linspace(lon1, lon2, steps)
            
            for lat, lon in zip(lats, lons):
                center_r, center_c = coord_to_grid_index(lat, lon, lat_grid, lon_grid)
                
                for dr in range(-width_cells_lat, width_cells_lat + 1):
                    for dc in range(-width_cells_lon, width_cells_lon + 1):
                        r, c = center_r + dr, center_c + dc
                        if 0 <= r < cost_grid.shape[0] and 0 <= c < cost_grid.shape[1]:
                            if width_km < 5:
                                cost_grid[r, c] = 1.2
                            elif width_km < 20:
                                cost_grid[r, c] = 1.0
                            else:
                                cost_grid[r, c] = 0.8
        
        waterways_added += 1
    
    return waterways_added

def find_nearest_navigable_cell(grid, start_node, max_search_radius=500):
    rows, cols = grid.shape
    r, c = start_node
    if 0 <= r < rows and 0 <= c < cols and grid[r, c] != np.inf:
        return start_node
    visited = set()
    queue = [(0, r, c)]
    while queue:
        dist, curr_r, curr_c = heapq.heappop(queue)
        if (curr_r, curr_c) in visited or dist > max_search_radius:
            continue
        visited.add((curr_r, curr_c))
        if 0 <= curr_r < rows and 0 <= curr_c < cols and grid[curr_r, curr_c] != np.inf:
            return (curr_r, curr_c)
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                new_r, new_c = curr_r + dr, curr_c + dc
                if (new_r, new_c) not in visited:
                    new_dist = dist + (1.414 if dr != 0 and dc != 0 else 1)
                    heapq.heappush(queue, (new_dist, new_r, new_c))
    return None

def create_adaptive_bounds(start_point, end_point, ds):
    global_min_lat = float(ds['lat'].min())
    global_max_lat = float(ds['lat'].max())
    global_min_lon = float(ds['lon'].min())
    global_max_lon = float(ds['lon'].max())
    
    start_lat, start_lon = start_point
    end_lat, end_lon = end_point
    
    lon_span = abs(end_lon - start_lon)
    lat_span = abs(end_lat - start_lat)
    
    if lon_span > 150 or (start_lon * end_lon < 0 and lon_span > 100):
        return global_min_lat, global_max_lat, global_min_lon, global_max_lon
    
    if lon_span > 60 or lat_span > 30:
        padding = min(35, max(20, lon_span * 0.25, lat_span * 0.35))
        min_lat = max(global_min_lat, min(start_lat, end_lat) - padding)
        max_lat = min(global_max_lat, max(start_lat, end_lat) + padding)
        min_lon = max(global_min_lon, min(start_lon, end_lon) - padding)
        max_lon = min(global_max_lon, max(start_lon, end_lon) + padding)
    else:
        padding = max(15, lon_span * 0.4, lat_span * 0.5)
        min_lat = max(global_min_lat, min(start_lat, end_lat) - padding)
        max_lat = min(global_max_lat, max(start_lat, end_lat) + padding)
        min_lon = max(global_min_lon, min(start_lon, end_lon) - padding)
        max_lon = min(global_max_lon, max(start_lon, end_lon) + padding)
    
    return min_lat, max_lat, min_lon, max_lon

def create_navigable_grid(elevation_data, min_depth):
    actual_min_depth = max(min_depth, GLOBAL_MIN_DEPTH)
    
    water_mask = elevation_data <= actual_min_depth
    land_mask = ~water_mask
    
    cost_grid = np.ones_like(elevation_data, dtype=np.float64)
    cost_grid[land_mask] = np.inf
    
    depth_90 = actual_min_depth * 0.9
    depth_70 = actual_min_depth * 0.7
    depth_50 = actual_min_depth * 0.5
    depth_30 = actual_min_depth * 0.3
    
    very_shallow = (elevation_data > depth_90) & water_mask
    cost_grid[very_shallow] = 50.0
    
    shallow = (elevation_data > depth_70) & (elevation_data <= depth_90)
    cost_grid[shallow] = 15.0
    
    moderate_shallow = (elevation_data > depth_50) & (elevation_data <= depth_70)
    cost_grid[moderate_shallow] = 5.0
    
    moderate_deep = (elevation_data > depth_30) & (elevation_data <= depth_50)
    cost_grid[moderate_deep] = 2.0
    
    deep_water = elevation_data <= depth_30
    cost_grid[deep_water & water_mask] = 1.0
    
    return cost_grid

def find_narrow_gaps(land_mask, max_gap_width=MAX_BRIDGE_GAP):
    gaps = []
    rows, cols = land_mask.shape
    
    for direction in ['horizontal', 'vertical']:
        if direction == 'horizontal':
            for r in range(rows):
                land_pixels = np.where(land_mask[r, :])[0]
                if len(land_pixels) < 2:
                    continue
                
                for i in range(len(land_pixels) - 1):
                    gap_start = land_pixels[i] + 1
                    gap_end = land_pixels[i + 1]
                    gap_width = gap_end - gap_start
                    
                    if 1 <= gap_width <= max_gap_width:
                        gaps.append({
                            'start': (r, gap_start),
                            'end': (r, gap_end - 1),
                            'width': gap_width,
                            'direction': 'horizontal'
                        })
        else:
            for c in range(cols):
                land_pixels = np.where(land_mask[:, c])[0]
                if len(land_pixels) < 2:
                    continue
                
                for i in range(len(land_pixels) - 1):
                    gap_start = land_pixels[i] + 1
                    gap_end = land_pixels[i + 1]
                    gap_width = gap_end - gap_start
                    
                    if 1 <= gap_width <= max_gap_width:
                        gaps.append({
                            'start': (gap_start, c),
                            'end': (gap_end - 1, c),
                            'width': gap_width,
                            'direction': 'vertical'
                        })
    
    return sorted(gaps, key=lambda x: x['width'])

def create_strait_passages(cost_grid, elevation_data, min_depth):
    land_mask = elevation_data > min_depth
    narrow_gaps = find_narrow_gaps(land_mask)
    
    passages_created = 0
    for gap in narrow_gaps[:100]:
        if gap['width'] <= MIN_STRAIT_WIDTH * 5:
            start_r, start_c = gap['start']
            end_r, end_c = gap['end']
            
            if gap['direction'] == 'horizontal':
                for c in range(start_c, end_c + 1):
                    for width_offset in range(-MIN_STRAIT_WIDTH, MIN_STRAIT_WIDTH + 1):
                        nr = start_r + width_offset
                        if 0 <= nr < cost_grid.shape[0]:
                            cost_grid[nr, c] = min(cost_grid[nr, c], 2.0)
            else:
                for r in range(start_r, end_r + 1):
                    for width_offset in range(-MIN_STRAIT_WIDTH, MIN_STRAIT_WIDTH + 1):
                        nc = start_c + width_offset
                        if 0 <= nc < cost_grid.shape[1]:
                            cost_grid[r, nc] = min(cost_grid[r, nc], 2.0)
            
            passages_created += 1
    
    return passages_created

def connect_water_components(cost_grid):
    water_mask = cost_grid != np.inf
    labeled_water, num_components = label(water_mask)
    
    if num_components <= 1:
        return 0
    
    component_sizes = []
    for i in range(1, num_components + 1):
        size = np.sum(labeled_water == i)
        component_sizes.append((size, i))
    
    component_sizes.sort(reverse=True)
    connections_made = 0
    
    main_component_label = component_sizes[0][1] if component_sizes else 1
    main_component_mask = labeled_water == main_component_label
    
    for size, component_label in component_sizes[1:]:
        if size < 50:
            continue
        
        component_mask = labeled_water == component_label
        
        main_coords = np.where(main_component_mask)
        comp_coords = np.where(component_mask)
        
        if len(main_coords[0]) == 0 or len(comp_coords[0]) == 0:
            continue
        
        main_sample = min(300, len(main_coords[0]))
        comp_sample = min(300, len(comp_coords[0]))
        
        main_indices = np.random.choice(len(main_coords[0]), main_sample, replace=False)
        comp_indices = np.random.choice(len(comp_coords[0]), comp_sample, replace=False)
        
        min_dist = float('inf')
        best_main = None
        best_comp = None
        
        for i in main_indices[:100]:
            main_r, main_c = main_coords[0][i], main_coords[1][i]
            for j in comp_indices[:100]:
                comp_r, comp_c = comp_coords[0][j], comp_coords[1][j]
                dist = np.sqrt((main_r - comp_r)**2 + (main_c - comp_c)**2)
                
                if dist < min_dist:
                    min_dist = dist
                    best_main = (main_r, main_c)
                    best_comp = (comp_r, comp_c)
        
        if min_dist <= MAX_BRIDGE_GAP * 1.5 and best_main and best_comp:
            main_r, main_c = best_main
            comp_r, comp_c = best_comp
            
            steps = max(abs(comp_r - main_r), abs(comp_c - main_c)) + 1
            rs = np.linspace(main_r, comp_r, steps).astype(int)
            cs = np.linspace(main_c, comp_c, steps).astype(int)
            
            channel_width = max(MIN_STRAIT_WIDTH, int(8 - min_dist / 25))
            
            for r, c in zip(rs, cs):
                for dr in range(-channel_width, channel_width + 1):
                    for dc in range(-channel_width, channel_width + 1):
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < cost_grid.shape[0] and 0 <= nc < cost_grid.shape[1]:
                            if cost_grid[nr, nc] == np.inf:
                                cost_grid[nr, nc] = 6.0
                            else:
                                cost_grid[nr, nc] = min(cost_grid[nr, nc], 2.5)
            
            connections_made += 1
            main_component_mask = main_component_mask | component_mask
    
    return connections_made

def enhance_shallow_connectivity(cost_grid, elevation_data, min_depth):
    slightly_deeper = min_depth * 0.85
    moderately_deeper = min_depth * 0.7
    
    extended_water = elevation_data <= slightly_deeper
    moderate_extended = elevation_data <= moderately_deeper
    
    current_water = cost_grid != np.inf
    new_water_areas = extended_water & ~current_water
    moderate_new_areas = moderate_extended & ~current_water & ~new_water_areas
    
    if np.any(new_water_areas):
        dilated_new = binary_dilation(new_water_areas, iterations=3)
        cost_grid[dilated_new & (cost_grid == np.inf)] = 20.0
    
    if np.any(moderate_new_areas):
        dilated_moderate = binary_dilation(moderate_new_areas, iterations=2)
        cost_grid[dilated_moderate & (cost_grid == np.inf)] = 35.0
    
    return np.sum(new_water_areas) + np.sum(moderate_new_areas)

def check_global_connectivity(cost_grid, start_idx, end_idx):
    water_mask = cost_grid != np.inf
    labeled_array, num_features = label(water_mask)
    
    if labeled_array[start_idx] == 0 or labeled_array[end_idx] == 0:
        return False, "Endpoints not in water"
    
    if labeled_array[start_idx] == labeled_array[end_idx]:
        return True, f"Connected: {np.sum(water_mask)} water cells"
    
    return False, f"Disconnected: {num_features} components"

def attempt_route_find(ds, start_point, end_point, min_depth_meters, subset_padding):
    try:
        bounds = create_adaptive_bounds(start_point, end_point, ds)
        min_lat_req, max_lat_req, min_lon_req, max_lon_req = bounds
        
        if ds['lat'].values[0] > ds['lat'].values[-1]:
            lat_slice = slice(max_lat_req, min_lat_req)
        else:
            lat_slice = slice(min_lat_req, max_lat_req)
        
        if ds['lon'].values[0] < ds['lon'].values[-1]:
            lon_slice = slice(min_lon_req, max_lon_req)
        else:
            lon_slice = slice(max_lon_req, min_lon_req)
        
        subset = ds.sel(lat=lat_slice, lon=lon_slice)
        
        if subset.sizes['lat'] == 0 or subset.sizes['lon'] == 0:
            return None, "Empty geographic subset"
        
        elevation_data = subset['elevation'].values
        if elevation_data.size == 0:
            return None, "No elevation data available"
        
        effective_min_depth = max(min_depth_meters, GLOBAL_MIN_DEPTH)
        water_cells = np.sum(elevation_data <= effective_min_depth)
        total_cells = elevation_data.size
        water_percentage = (water_cells / total_cells) * 100
        
        if water_percentage < 0.05:
            return None, f"Insufficient water: {water_percentage:.2f}%"
        
        max_dimension = max(elevation_data.shape)
        scale_factor = 1
        if max_dimension > 3000:
            scale_factor = max_dimension // 2500
        elif max_dimension > 2000:
            scale_factor = 2
        elif max_dimension > 1200:
            scale_factor = max_dimension // 1000
        
        if scale_factor > 1:
            scaled_elevation = elevation_data[::scale_factor, ::scale_factor]
            scaled_lat = subset['lat'].values[::scale_factor]
            scaled_lon = subset['lon'].values[::scale_factor]
        else:
            scaled_elevation = elevation_data
            scaled_lat = subset['lat'].values
            scaled_lon = subset['lon'].values
        
        cost_grid = create_navigable_grid(scaled_elevation, effective_min_depth)
        
        waterways_added = add_waterway_passages(cost_grid, scaled_lat, scaled_lon)
        straits_created = create_strait_passages(cost_grid, scaled_elevation, effective_min_depth)
        shallow_areas = enhance_shallow_connectivity(cost_grid, scaled_elevation, effective_min_depth)
        connections = connect_water_components(cost_grid)
        
        def coord_to_index(lat, lon, grid_lat, grid_lon):
            lat_idx = np.abs(grid_lat - lat).argmin()
            lon_idx = np.abs(grid_lon - lon).argmin()
            return int(lat_idx), int(lon_idx)
        
        start_idx = coord_to_index(start_point[0], start_point[1], scaled_lat, scaled_lon)
        end_idx = coord_to_index(end_point[0], end_point[1], scaled_lat, scaled_lon)
        
        search_radius = min(1000, max(cost_grid.shape) // 2)
        nav_start = find_nearest_navigable_cell(cost_grid, start_idx, search_radius)
        if nav_start is None:
            return None, "No navigable water near start"
        
        nav_end = find_nearest_navigable_cell(cost_grid, end_idx, search_radius)
        if nav_end is None:
            return None, "No navigable water near end"
        
        if nav_start == nav_end:
            return None, "Start and end are identical"
        
        is_connected, conn_msg = check_global_connectivity(cost_grid, nav_start, nav_end)
        if not is_connected:
            return None, f"Not connected: {conn_msg} (waterways:{waterways_added}, straits:{straits_created}, connections:{connections})"
        
        try:
            path_indices, total_cost = route_through_array(
                cost_grid, nav_start, nav_end, 
                fully_connected=True, geometric=True
            )
            
            if not path_indices or len(path_indices) < 2:
                path_indices, total_cost = route_through_array(
                    cost_grid, nav_start, nav_end, 
                    fully_connected=True, geometric=False
                )
            
            if not path_indices or len(path_indices) < 2:
                return None, "Pathfinding algorithm failed"
            
            path_coords = []
            for r, c in path_indices:
                if 0 <= r < len(scaled_lat) and 0 <= c < len(scaled_lon):
                    path_coords.append([float(scaled_lat[r]), float(scaled_lon[c])])
            
            if len(path_coords) < 2:
                return None, "Invalid coordinate conversion"
            
            total_distance = 0
            for i in range(1, len(path_coords)):
                lat1, lon1 = path_coords[i-1]
                lat2, lon2 = path_coords[i]
                dlat = np.radians(lat2 - lat1)
                dlon = np.radians(lon2 - lon1)
                a = (np.sin(dlat/2)**2 + 
                     np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * 
                     np.sin(dlon/2)**2)
                total_distance += 6371 * 2 * np.arcsin(np.sqrt(a))
            
            return path_coords, f"Route found: {len(path_coords)} waypoints, {total_distance:.0f}km, waterways:{waterways_added}, scale:{scale_factor}"
            
        except Exception as e:
            return None, f"Pathfinding execution failed: {str(e)}"
    
    except Exception as e:
        return None, f"Route computation failed: {str(e)}"