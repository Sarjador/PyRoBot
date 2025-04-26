#include <Keyboard.h>
#include <Mouse.h>

void setup() {
  Serial.begin(9600);
  Keyboard.begin();
  Mouse.begin();
}

void loop() {
  if (!Serial.available()) return;
  String cmd = Serial.readStringUntil('\n');
  cmd.trim();

  // Clic izquierdo
  if (cmd == "CLICK") {
    Mouse.click(MOUSE_LEFT);
  }
  // Movimiento relativo
  else if (cmd.startsWith("MOVE:")) {
    // Formato: MOVE:dx,dy
    int comma = cmd.indexOf(',');
    if (comma > 5) {
      int dx = cmd.substring(5, comma).toInt();
      int dy = cmd.substring(comma + 1).toInt();
      // Mueve el ratón una vez. Si necesitas una gran distancia, haz varios MOVE pequeños
      Mouse.move(dx, dy);
      // Opcional: un pequeño delay para que Windows procese el movimiento
      delay(10);
    }
  }
  // Pulsación simple de tecla (Z, X, etc.)
  else if (cmd.length() == 1) {
    char k = cmd.charAt(0);
    Keyboard.press(k);
    delay(50);
    Keyboard.release(k);
  }
  // Teclas de función F1-F12
  else if (cmd.startsWith("F")) {
    int fn = cmd.substring(1).toInt();
    if (fn >= 1 && fn <= 12) {
      Keyboard.press(KEY_F1 + fn - 1);
      delay(50);
      Keyboard.release(KEY_F1 + fn - 1);
    }
  }
}
