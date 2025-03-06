// Function to evaluate a polynomial using Horner's method
float horner(float x, float coeffs[], int degree) {
  float result = coeffs[0]; // Start with the highest-degree coefficient
  for (int i = 1; i <= degree; i++) {
    result = result * x + coeffs[i];
  }
  return result;
}

float Th(float H) {
  float B = 2900.0;
  float coeffs[] = { 0.65360594, -2.45201911,  3.66681941, -2.87040581,  1.27712266, -0.35692813,  0.15802103 };
  int degree = 6; // Degree of the polynomial
  float result = horner(H, coeffs, degree);
  return result*B;
}

void setup() {
  Serial.begin(115200);
  int N = 1000;
  for (float H = 0.1; H < 0.9; H+=0.8/N) {
    float T = Th(H);
    Serial.print(H, 8);
    Serial.print(", ");
    Serial.println(T, 8);
  }
}

void loop() {
  // Nothing to do here
}
