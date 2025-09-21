import 'dart:io';
import 'dart:convert';
import 'package:http/http.dart' as http;
class Box {
  final int? x1;
  final int? y1;
  final int? x2;
  final int? y2;
  final int? veri;
  Box({
    required this.x1,
    required this.y1,
    required this.x2,
    required this.y2,
    required this.veri
  });

  factory Box.fromJson(Map<String, dynamic> json) {
    return Box(
      x1: json["x1"],
      y1: json["y1"],
      x2: json["x2"],
      y2: json["y2"],
      veri: json["veri"]
    );
  }
}
void main() async {

  // Exemplo POST → envia dados para /process do Flask
  File file = File('C:/Users/alunos/Desktop/projete/client/bin/img2.jpeg');
  List<int> imageBytes = await file.readAsBytes();
  String base64Image = base64Encode(imageBytes);

  var postUrl = Uri.parse('http://127.0.0.1:5000/process');
  var postResponse = await http.post(
    postUrl,
    headers: {"Content-Type": "application/json"},
    body: jsonEncode({
      "imagem":base64Image
    }), // Dados enviados em JSON
  );

    var data = jsonDecode(postResponse.body);
    print(data);
    List<dynamic> boxesJson = data["boxes"];

    List<Box> boxes = boxesJson.map((b) => Box.fromJson(b)).toList();
    for (var b in boxes) {
      print("Box => x1:${b.x1}, y1:${b.y1}, x2:${b.x2}, y2:${b.y2}, veri:${b.veri}");
    }
}
