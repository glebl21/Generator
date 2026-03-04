 (cd "$(git rev-parse --show-toplevel)" && git apply --3way <<'EOF' 
diff --git a/Dockerfile b/Dockerfile
index 594f1fe99e068dec9150a5dcf7a3eb264a0feb07..550b16ac5a5b735b68790827cddc0e5e23a07ef3 100644
--- a/Dockerfile
+++ b/Dockerfile
@@ -1,12 +1,15 @@
 FROM python:3.11-slim
 
 WORKDIR /app
 
 # Зависимости
 COPY requirements.txt .
 RUN pip install --no-cache-dir -r requirements.txt
 
 # Копируем бота
 COPY bot.py .
 
+# Проверка синтаксиса на этапе сборки (ловит случайно повреждённый bot.py)
+RUN python -m py_compile bot.py
+
 CMD ["python", "bot.py"]
 
EOF
)
