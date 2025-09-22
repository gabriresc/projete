import 'dart:convert';
import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:file_picker/file_picker.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return const MaterialApp(
      debugShowCheckedModeBanner: false,
      home: DetectionViewer(),
    );
  }
}

class DetectionViewer extends StatefulWidget {
  const DetectionViewer({super.key});

  @override
  DetectionViewerState createState() => DetectionViewerState();
}

class DetectionViewerState extends State<DetectionViewer> {
  Uint8List? imageBytes; // imagem a exibir (recebida do backend)
  Uint8List? selectedImageBytes; // imagem selecionada pelo FilePicker
  List<Box> boxes = [];

  /// Seleciona uma imagem do computador
  Future<void> _pickImage() async {
    FilePickerResult? result = await FilePicker.platform.pickFiles(
      type: FileType.image,
    );

    if (result != null && result.files.single.bytes != null) {
      setState(() {
        selectedImageBytes = result.files.single.bytes!;
      });
    }
  }

  /// Envia a imagem selecionada para o backend e recebe imagem + boxes
  Future<void> _processImage() async {
    if (selectedImageBytes == null) return;

    try {
      String base64Image = base64Encode(selectedImageBytes!);
      var postUrl = Uri.parse('http://127.0.0.1:5000/process');
      var postResponse = await http.post(
        postUrl,
        headers: {"Content-Type": "application/json"},
        body: jsonEncode({"imagem": base64Image}),
      );

      if (postResponse.statusCode == 200) {
        var data = jsonDecode(postResponse.body);

        // Recebe a imagem do backend em Base64
        String receivedBase64 = data['img'];
        List<dynamic> boxesJson = data['boxes'];

        setState(() {
          imageBytes = base64Decode(receivedBase64);
          boxes = boxesJson.map((b) => Box.fromJson(b)).toList();
        });
      } else {
        debugPrint("Erro ao processar: ${postResponse.statusCode}");
      }
    } catch (e) {
      debugPrint("Erro ao processar: $e");
    }
  }

  /// Edita o nome de uma box
  void _onBoxTap(int index) async {
    final controller = TextEditingController(text: boxes[index].name);

    String? newName = await showDialog<String>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text("Nomear área"),
        content: TextField(
          controller: controller,
          decoration: const InputDecoration(hintText: "Digite o nome"),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, null),
            child: const Text("Cancelar"),
          ),
          ElevatedButton(
            onPressed: () => Navigator.pop(context, controller.text),
            child: const Text("Salvar"),
          ),
        ],
      ),
    );

    if (newName != null && newName.isNotEmpty) {
      setState(() {
        boxes[index].name = newName;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Detecção de Áreas")),
      body: Center(
        child: imageBytes == null
            ? const Text("Nenhuma imagem processada ainda")
            : Stack(
                children: [
                  Image.memory(imageBytes!, fit: BoxFit.contain),
                  ...boxes.asMap().entries.map((entry) {
                    int index = entry.key;
                    Box box = entry.value;

                    return Positioned(
                      left: box.x1!.toDouble(),
                      top: box.y1!.toDouble(),
                      child: GestureDetector(
                        onTap: () => _onBoxTap(index),
                        child: Container(
                          width: (box.x2! - box.x1!).toDouble(),
                          height: (box.y2! - box.y1!).toDouble(),
                          decoration: BoxDecoration(
                            border: Border.all(color: Colors.red, width: 2),
                            color: Colors.red.withValues(alpha: 0.1),
                          ),
                          child: Align(
                            alignment: Alignment.topLeft,
                            child: Text(
                              box.name,
                              style: const TextStyle(
                                fontSize: 12,
                                color: Colors.black,
                                backgroundColor: Colors.white70,
                              ),
                            ),
                          ),
                        ),
                      ),
                    );
                  }),
                ],
              ),
      ),
      floatingActionButton: Column(
        mainAxisAlignment: MainAxisAlignment.end,
        children: [
          FloatingActionButton(
            heroTag: "pick",
            onPressed: _pickImage,
            tooltip: "Selecionar Imagem",
            child: const Icon(Icons.image),
          ),
          const SizedBox(height: 10),
          FloatingActionButton(
            heroTag: "process",
            onPressed: _processImage,
            tooltip: "Processar Imagem",
            child: const Icon(Icons.send),
          ),
        ],
      ),
    );
  }
}

// =====================
// Classe Box
// =====================
class Box {
  final int? x1;
  final int? y1;
  final int? x2;
  final int? y2;
  final int? veri;
  String name;

  Box({
    required this.x1,
    required this.y1,
    required this.x2,
    required this.y2,
    required this.veri,
    this.name = "Sem nome",
  });

  factory Box.fromJson(Map<String, dynamic> json) {
    return Box(
      x1: json["x1"],
      y1: json["y1"],
      x2: json["x2"],
      y2: json["y2"],
      veri: json["veri"],
      name: json["name"] ?? "Sem nome",
    );
  }

  Map<String, dynamic> toJson() {
    return {
      "x1": x1,
      "y1": y1,
      "x2": x2,
      "y2": y2,
      "veri": veri,
      "name": name,
    };
  }
}
