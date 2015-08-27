int pinOut;

void setup() {
  // put your setup code here, to run once:  
  Serial.begin(9600); // S
  
  //Set all pins (2 through 12) to output mode
  for(int ii = 2; ii < 12; ii++){
    pinMode(ii, OUTPUT);
    delay(5);
  }
  
  
}

void loop() {
  
  //Get which pin 
  pinOut = Serial.parseInt(); //Defaults to 0 if times out.
  
  // If an integer is received, send a TTL pulse on that port.
  if (pinOut > 0){
  
    Serial.print(pinOut);
  
    digitalWrite(pinOut, HIGH);
    delay(40);
    
    digitalWrite(pinOut, LOW);
    delay(40);    
  }
  
 
}
