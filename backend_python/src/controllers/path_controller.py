from flask import request, jsonify, current_app
from src.utils import pathfinder

def find_path_controller():
    print(">> Flask /path/find hit")

    dataset = current_app.config.get('GEBCO_DATASET')
    if dataset is None:
        print(">> Dataset is not loaded")
        return jsonify({"status": "error", "message": "Dataset not loaded. Cannot process request."}), 503

    data = request.get_json()
    print(">> Received data:", data)

    if not data or 'start' not in data or 'end' not in data:
        print(">> Invalid request body")
        return jsonify({"status": "error", "message": "Invalid request body."}), 400

    try:
        start_coords = (float(data['start']['lat']), float(data['start']['lng']))
        end_coords = (float(data['end']['lat']), float(data['end']['lng']))
    except (ValueError, TypeError):
        print(">> Invalid coordinate format")
        return jsonify({"status": "error", "message": "Invalid coordinate format."}), 400

    print(">> Start coords:", start_coords)
    print(">> End coords:", end_coords)

    cache = current_app.config['ROUTE_CACHE']
    cache_key = (start_coords, end_coords)

    if cache_key in cache:
        print(">> Returning cached result")
        cached_result = cache[cache_key]
        cached_result['message'] += " (from cache)"
        return jsonify(cached_result)

    padding_levels = [2.5, 5.0, 8.0, 12.0, 18.0, 25.0, 35.0, 50.0]
    depth_levels = [-30.0, -25.0, -20.0, -15.0, -12.0, -10.0, -8.0, -6.0, -4.0, -2.0]

    all_errors = []
    
    for pad in padding_levels:
        for depth in depth_levels:
            print(f">> Trying pathfind with depth={depth}, pad={pad}")
            route, message = pathfinder.attempt_route_find(
                ds=dataset,
                start_point=start_coords,
                end_point=end_coords,
                min_depth_meters=depth,
                subset_padding=pad
            )
            
            if route:
                print(">> Route found")
                result = {
                    "status": "success",
                    "message": message,
                    "path": route
                }
                cache[cache_key] = result
                return jsonify(result)
            else:
                all_errors.append(f"Depth {depth}m, Pad {pad}°: {message}")
                print(f">> Failed: {message}")

    print(">> No valid route found after all attempts")
    
    error_summary = f"Failed after {len(padding_levels) * len(depth_levels)} attempts. "
    if len(all_errors) > 0:
        error_summary += f"Final attempts: {'; '.join(all_errors[-3:])}"
    else:
        error_summary += "No detailed error information available."
    
    return jsonify({
        "status": "error",
        "message": error_summary,
        "attempts": len(all_errors),
        "start_coords": start_coords,
        "end_coords": end_coords
    }), 422