 #version 330
 out vec4 final_color;
 uniform vec3 diffuse;
 float brightness;
 float width = 5.;

 float pi = 3.14159;

 void main()
 {
    brightness = sin(gl_FragCoord.x / width) / 2. + .5;
    brightness *= (1. / (50. * sqrt(2 * pi))) * exp(-.5 * pow(((gl_FragCoord.x - 300.) / 50.), 2));
    final_color = vec4(vec3(brightness), 1.);
 }