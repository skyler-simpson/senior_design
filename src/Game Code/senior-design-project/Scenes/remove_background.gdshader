shader_type canvas_item;

// The color you want to make transparent (defaults to pure green)
uniform vec4 chroma_key_color : source_color = vec4(0.0, 1.0, 0.0, 1.0); 
// How strict the color matching should be (higher = removes more nearby colors)
uniform float tolerance : hint_range(0.0, 1.0) = 0.2; 

void fragment() {
    // Get the current pixel's color
    vec4 current_color = texture(TEXTURE, UV);
    
    // Calculate how close the pixel's color is to our green screen color
    float color_distance = distance(current_color.rgb, chroma_key_color.rgb);
    
    // If the color is extremely close to our green screen, make it invisible
    if (color_distance < tolerance) {
        COLOR = vec4(0.0); // Sets Alpha (transparency) to 0
    } else {
        COLOR = current_color; // Keep the character's pixels visible
    }
}// Uncomment to replace the default light processing function with this one.
//}
