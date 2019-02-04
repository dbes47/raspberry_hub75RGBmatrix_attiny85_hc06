#include <SoftwareSerial.h>
#include <dht.h>

dht DHT;
#define DHT_PIN 0

SoftwareSerial blue(4,3);

void setup() {
  blue.begin(9600);
}

void loop() {
  // put your main code here, to run repeatedly:
  // READ DATA
  int chk = DHT.read22(DHT_PIN);
  switch (chk)
  {
    case DHTLIB_OK:
      blue.print("<hum>");
      blue.print(DHT.humidity);
      blue.print("</hum><temp>");
      blue.print(DHT.temperature);
      blue.println("</temp>");
      break;
    case DHTLIB_ERROR_CHECKSUM:
      blue.print("Checksum error,\t");
      break;
    case DHTLIB_ERROR_TIMEOUT:
      blue.print("Time out error,\t");
      break;
    case DHTLIB_ERROR_CONNECT:
      blue.print("Connect error,\t");
      break;
    case DHTLIB_ERROR_ACK_L:
      blue.print("Ack Low error,\t");
      break;
    case DHTLIB_ERROR_ACK_H:
      blue.print("Ack High error,\t");
      break;
    default:
      blue.print("Unknown error,\t");
      break;
  }
  // DISPLAY DATA


  delay(3000);
}
