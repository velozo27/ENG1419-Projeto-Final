#include <Servo.h>
#include <TimerOne.h>

// Servos
Servo servo1;
Servo servo2;
Servo servo3;

// Posição dos servos em graus
int angulo_servo1 = 90;
int angulo_servo2 = 90;
int angulo_servo3 = 90;

/*Modo 1 : modo varredura
  Modo 2 : modo manual*/
int modo = 2;

// Para limitar a viagem dos servos
int limite_alta = 170;
int limite_baixa = 5;
int limite_direita = 5;
int limite_esquerda = 170;

// MODO MANUAL
// Controlar a velocidad dos servos
int delta_controle_servo1 = 5;
int delta_controle_servo2 = 10;
int delta_controle_servo3 = 10;

// MODO VARREDURA
// Direção da rotação
bool direcao_servo2 = true;
bool direcao_servo3 = true;

// sensor_de_movimento
int sensor_de_movimento = 2;

// sensor_de_luz
int sensor_de_luz = A0;
bool esta_dia = 1;
unsigned long instanteAnterior_debounce2 = 0;

// Debounce da interrupção
unsigned long instanteAnterior_debounce = 0;

void setup()
{

  Serial.begin(9600);

  // servo1.attach(4, 1000, 2000); //na simulaçao
  // servo2.attach(5, 1000, 2000);
  servo1.attach(4);
  servo2.attach(5);
  servo3.attach(6);

  servo1.write(angulo_servo1);
  servo2.write(angulo_servo2);
  servo3.write(angulo_servo3);

  // Timer para o modo varredura
  Timer1.initialize(500000); // ms  ==> velocidade do servo : 2 grau/s
  Timer1.attachInterrupt(fn_varredura);
  Timer1.stop();

  // sensor de movimiento com um interrupt
  pinMode(sensor_de_movimento, INPUT);
  int origem = digitalPinToInterrupt(sensor_de_movimento);
  attachInterrupt(origem, fn_movimento, CHANGE);

  // sensor de luz
  pinMode(sensor_de_luz, INPUT);
}

void loop()
{

  int luz_mesurada = map(analogRead(sensor_de_luz), 0, 1023, 0, 100);

  if (millis() > instanteAnterior_debounce2 + 100)
  {
    if (esta_dia)
    {
      if (luz_mesurada < 20)
      {
        esta_dia = 0;
        Serial.println("noite");
      }
    }
    else
    {
      if (luz_mesurada >= 20)
      {
        esta_dia = 1;
        Serial.println("dia");
      }
    }

    instanteAnterior_debounce2 = millis();
  }

  if (Serial.available() > 0)
  {
    String texto = Serial.readStringUntil('\n');
    texto.trim();

    if (texto == "varredura")
    {
      modo = 1;
      Timer1.start();
    }
    else if (texto == "manual")
    {
      modo = 2;
      Timer1.stop();
    }

    // Modo manual
    if (modo == 2)
    {

      if (texto == "cima 1")
      {

        angulo_servo1 += delta_controle_servo1;

        if (angulo_servo1 >= limite_alta)
        {
          angulo_servo1 = limite_alta;
        }

        servo1.write(angulo_servo1);
      }
      else if (texto == "baixo 1")
      {

        angulo_servo1 -= delta_controle_servo1;

        if (angulo_servo1 <= limite_baixa)
        {
          angulo_servo1 = limite_baixa;
        }

        servo1.write(angulo_servo1);
      }
      else if (texto == "direita 1")
      {

        angulo_servo2 -= delta_controle_servo2;

        if (angulo_servo2 <= limite_direita)
        {
          angulo_servo2 = limite_direita;
        }

        servo2.write(angulo_servo2);
      }
      else if (texto == "esquerda 1")
      {

        angulo_servo2 += delta_controle_servo2;

        if (angulo_servo2 >= limite_esquerda)
        {
          angulo_servo2 = limite_esquerda;
        }

        servo2.write(angulo_servo2);
      }
      else if (texto == "direita 2")
      {

        angulo_servo3 -= delta_controle_servo3;

        if (angulo_servo3 <= limite_direita)
        {
          angulo_servo3 = limite_direita;
        }

        servo3.write(angulo_servo3);
      }
      else if (texto == "esquerda 2")
      {

        angulo_servo3 += delta_controle_servo3;

        if (angulo_servo3 >= limite_esquerda)
        {
          angulo_servo3 = limite_esquerda;
        }

        servo3.write(angulo_servo3);
      }
    }
  }

  // Serial.println("Servo 1: " + String(angulo_servo1) + " Servo 2: " + String(angulo_servo2));
}

void fn_varredura(void)
{

  if (direcao_servo2)
  {
    angulo_servo2 -= 1;
    if (angulo_servo2 <= limite_direita)
    {
      angulo_servo2 = limite_direita;
      direcao_servo2 = false;
    }
  }
  else
  {
    angulo_servo2 += 1;
    if (angulo_servo2 >= limite_esquerda)
    {
      angulo_servo2 = limite_esquerda;
      direcao_servo2 = true;
    }
  }
  servo2.write(angulo_servo2);

  if (direcao_servo3)
  {
    angulo_servo3 -= 1;
    if (angulo_servo3 <= limite_direita)
    {
      angulo_servo3 = limite_direita;
      direcao_servo3 = false;
    }
  }
  else
  {
    angulo_servo3 += 1;
    if (angulo_servo3 >= limite_esquerda)
    {
      angulo_servo3 = limite_esquerda;
      direcao_servo3 = true;
    }
  }
  servo3.write(angulo_servo3);
}

void fn_movimento(void)
{

  if (millis() > instanteAnterior_debounce + 10)
  {

    if (digitalRead(sensor_de_movimento))
    {
      Serial.println("Movimento detectado");
    }
    else
    {
      Serial.println("Sem movimento");
    }

    instanteAnterior_debounce = millis();
  }
}
