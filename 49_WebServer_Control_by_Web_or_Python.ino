// ESP32_WebServer.ino
#include <WiFi.h>
#include <WebServer.h>
#include <ArduinoJson.h>

// WiFi配置
const char* ssid = "Tom";
const char* password = "11111111";

// 创建Web服务器对象，端口80
WebServer server(80);

// 引脚定义
const int ledPin = 27;       // LED
const int relayPin = 4;     // 继电器控制
const int analogPin = 34;   // 模拟输入
const int buttonPin = 35;   // 按钮输入

// 设备状态变量
bool ledState = false;
bool relayState = false;
int analogValue = 0;
bool buttonState = false;

void setup() {
  Serial.begin(115200);
  
  // 初始化GPIO
  pinMode(ledPin, OUTPUT);
  pinMode(relayPin, OUTPUT);
  pinMode(buttonPin, INPUT);
  digitalWrite(ledPin, LOW);
  digitalWrite(relayPin, LOW);
  
  // 连接WiFi
  connectToWiFi();
  
  // 设置API路由
  setupRoutes();
  
  // 启动服务器
  server.begin();
  Serial.println("HTTP服务器已启动");
  printNetworkInfo();
}

void loop() {
  server.handleClient();  // 处理客户端请求
  updateSensorData();     // 更新传感器数据
  delay(10);
}

void connectToWiFi() {
  Serial.println();
  Serial.print("连接WiFi: ");
  Serial.println(ssid);
  
  WiFi.begin(ssid, password);
  
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  
  Serial.println();
  Serial.println("WiFi连接成功!");
}

String html = 
"<html>\n"
"  <head>\n"
"    <title>ESP32控制服务器</title>\n"
"    <meta charset=\"UTF-8\">\n"
"    <style>\n"
"      body { font-family: Arial; margin: 40px; }\n"
"      .endpoint { background: #f5f5f5; padding: 15px; margin: 10px 0; border-radius: 5px; }\n"
"      button { padding: 10px 15px; margin: 5px; cursor: pointer; }\n"
"      .on { background: #4CAF50; color: white; }\n"
"      .off { background: #f44336; color: white; }\n"
"    </style>\n"
"  </head>\n"
"  <body>\n"
"    <h1>ESP32控制服务器</h1>\n"
"    <p><strong>设备IP:</strong> " + WiFi.localIP().toString() + "</p>\n"
"    \n"
"    <div class=\"endpoint\">\n"
"      <h3>📊 获取设备信息</h3>\n"
"      <p><strong>GET</strong> <code>/api/device/info</code></p>\n"
"      <button onclick=\"fetchData('/api/device/info')\">获取信息</button>\n"
"    </div>\n"
"    \n"
"    <div class=\"endpoint\">\n"
"      <h3>💡 LED控制</h3>\n"
"      <p><strong>GET</strong> <code>/api/led/on</code> | <code>/api/led/off</code> | <code>/api/led/toggle</code></p>\n"
"      <button class=\"on\" onclick=\"fetchData('/api/led/on')\">打开LED</button>\n"
"      <button class=\"off\" onclick=\"fetchData('/api/led/off')\">关闭LED</button>\n"
"      <button onclick=\"fetchData('/api/led/toggle')\">切换LED</button>\n"
"    </div>\n"
"    \n"
"    <div class=\"endpoint\">\n"
"      <h3>🔌 继电器控制</h3>\n"
"      <p><strong>GET</strong> <code>/api/relay/on</code> | <code>/api/relay/off</code></p>\n"
"      <button class=\"on\" onclick=\"fetchData('/api/relay/on')\">打开继电器</button>\n"
"      <button class=\"off\" onclick=\"fetchData('/api/relay/off')\">关闭继电器</button>\n"
"    </div>\n"
"    \n"
"    <div class=\"endpoint\">\n"
"      <h3>📈 传感器数据</h3>\n"
"      <p><strong>GET</strong> <code>/api/sensor/data</code></p>\n"
"      <button onclick=\"fetchData('/api/sensor/data')\">读取传感器</button>\n"
"    </div>\n"
"    \n"
"    <div id=\"result\" style=\"margin-top: 20px; padding: 15px; background: #e8f4fd; border-radius: 5px;\"></div>\n"
"    \n"
"    <script>\n"
"      async function fetchData(url) {\n"
"        try {\n"
"          const response = await fetch(url);\n"
"          const data = await response.json();\n"
"          document.getElementById('result').innerHTML = '<pre>' + JSON.stringify(data, null, 2) + '</pre>';\n"
"        } catch (error) {\n"
"          document.getElementById('result').innerHTML = '错误: ' + error;\n"
"        }\n"
"      }\n"
"    </script>\n"
"  </body>\n"
"</html>";

void setupRoutes() {
  // 根路径 - 显示API文档
  server.on("/", HTTP_GET, []() {
    server.send(200, "text/html", html);
  });

  // 获取设备信息
  server.on("/api/device/info", HTTP_GET, []() {
    DynamicJsonDocument doc(1024);
    doc["device"] = "ESP32";
    doc["ip"] = WiFi.localIP().toString();
    doc["mac"] = WiFi.macAddress();
    doc["free_heap"] = ESP.getFreeHeap();
    doc["chip_id"] = ESP.getEfuseMac();
    
    String response;
    serializeJson(doc, response);
    server.send(200, "application/json", response);
  });

  // LED控制
  server.on("/api/led/on", HTTP_GET, []() {
    digitalWrite(ledPin, HIGH);
    ledState = true;
    sendSuccessResponse("LED已打开");
  });

  server.on("/api/led/off", HTTP_GET, []() {
    digitalWrite(ledPin, LOW);
    ledState = false;
    sendSuccessResponse("LED已关闭");
  });

  server.on("/api/led/toggle", HTTP_GET, []() {
    ledState = !ledState;
    digitalWrite(ledPin, ledState);
    sendSuccessResponse(ledState ? "LED已打开" : "LED已关闭");
  });

  // 继电器控制
  server.on("/api/relay/on", HTTP_GET, []() {
    digitalWrite(relayPin, HIGH);
    relayState = true;
    sendSuccessResponse("继电器已打开");
  });

  server.on("/api/relay/off", HTTP_GET, []() {
    digitalWrite(relayPin, LOW);
    relayState = false;
    sendSuccessResponse("继电器已关闭");
  });

  // 传感器数据
  server.on("/api/sensor/data", HTTP_GET, []() {
    DynamicJsonDocument doc(512);
    doc["analog_value"] = analogValue;
    doc["voltage"] = (analogValue * 3.3) / 4095.0;
    doc["button_pressed"] = buttonState;
    doc["led_state"] = ledState;
    doc["relay_state"] = relayState;
    
    String response;
    serializeJson(doc, response);
    server.send(200, "application/json", response);
  });

  // 未找到的路由
  server.onNotFound([]() {
    DynamicJsonDocument doc(256);
    doc["error"] = true;
    doc["message"] = "API端点不存在";
    
    String response;
    serializeJson(doc, response);
    server.send(404, "application/json", response);
  });
}

void sendSuccessResponse(const String& message) {
  DynamicJsonDocument doc(256);
  doc["success"] = true;
  doc["message"] = message;
  doc["led_state"] = ledState;
  doc["relay_state"] = relayState;
  
  String response;
  serializeJson(doc, response);
  server.send(200, "application/json", response);
}

void updateSensorData() {
  analogValue = analogRead(analogPin);
  buttonState = digitalRead(buttonPin);
}

void printNetworkInfo() {
  Serial.println("=== 网络信息 ===");
  Serial.print("IP地址: ");
  Serial.println(WiFi.localIP());
  Serial.print("MAC地址: ");
  Serial.println(WiFi.macAddress());
  Serial.print("信号强度: ");
  Serial.print(WiFi.RSSI());
  Serial.println(" dBm");
  Serial.println("================");
}
