
#include <Servo.h>

Servo servo1;
Servo servo2;

int angulo_servo1 = 90;
int angulo_servo2 = 90;

int limite_alta = 170;
int limite_baixa = 5;
int limite_direita = 170;
int limite_esquerda = 5;

int delta_controle = 10;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);

  //servo1.attach(4, 1000, 2000); na simulaçao
  //servo2.attach(5, 1000, 2000);
  servo1.attach(4);
  servo2.attach(5);

  servo1.write(angulo_servo1);
  servo2.write(angulo_servo2);
}

void loop() {
  // put your main code here, to run repeatedly:
  if (Serial.available() > 0) {
    String texto = Serial.readStringUntil('\n');
    texto.trim();

    

    if (texto == "baixa") {

      angulo_servo1 += delta_controle;

      if (angulo_servo1 >= limite_alta) {
        angulo_servo1 = limite_alta;
      }

      servo1.write(angulo_servo1);

    }
    else if (texto == "sube") {

      angulo_servo1 -= delta_controle;

      if (angulo_servo1 <= limite_baixa) {
        angulo_servo1 = limite_baixa;
      }

      servo1.write(angulo_servo1);

    }
    else if (texto == "direita") {

      angulo_servo2 += delta_controle;

      if (angulo_servo2 >= limite_direita) {
        angulo_servo2 = limite_direita;
      }

      servo2.write(angulo_servo2);

    }
    else if (texto == "esquerda") {

      angulo_servo2 -= delta_controle;

      if (angulo_servo2 <= limite_esquerda) {
        angulo_servo2 = limite_esquerda;
      }

      servo2.write(angulo_servo2);

    }
    
  }
  
  Serial.println("Servo 1: "+String(angulo_servo1)+" Servo 2: "+String(angulo_servo2));
}
