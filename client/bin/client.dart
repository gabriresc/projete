import 'dart:io';
import 'dart:convert';
import 'package:http/http.dart' as http;

void main() async {

  // Exemplo POST → envia dados para /process do Flask
  File file = File('C:/Users/gabri/Downloads/projete/client/bin/img2.jpeg');
  List<int> imageBytes = await file.readAsBytes();
  String base64Image = base64Encode(imageBytes);

  var postUrl = Uri.parse('http://127.0.0.1:5000/process');
  var postResponse = await http.post(
    postUrl,
    headers: {"Content-Type": "application/json"},
    body: jsonEncode({
      "nome": "Gabriel",
      "imagem":base64Image
    }), // Dados enviados em JSON
  );

  print('Resposta POST: ${postResponse.body}');
}
