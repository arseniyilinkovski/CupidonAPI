import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import numpy as np

# 📌 Параметры
IMG_SIZE = (224, 224)
BATCH_SIZE = 32
EPOCHS = 10
DATA_DIR = "D:/my_projects/cupidon_api/src/ai-models/training/dataset"
MODEL_PATH = "D:/my_projects/cupidon_api/src/ai-models/nsfw_model.h5"
SAVE_PATH = "D:/my_projects/cupidon_api/src/ai-models/nsfw_model_finetuned.h5"

# 🔁 Функция инверсии
def invert_image(x):
    return 1.0 - x

# 🔁 Функция добавления случайного шума
def add_noise(x):
    noise = tf.random.normal(shape=tf.shape(x), mean=0.0, stddev=0.05)
    return tf.clip_by_value(x + noise, 0.0, 1.0)

# 🔁 Комбинированная функция
def advanced_preprocessing(x):
    x = invert_image(x)
    x = add_noise(x)
    return x

# 🔧 Загружаем модель
print("🔧 Загружаем базовую модель...")
model = load_model(MODEL_PATH)
for layer in model.layers:
    layer.trainable = True
# 📦 Генераторы
print("📦 Подготавливаем датасет...")

# Обычные изображения с расширенной аугментацией
datagen_normal = ImageDataGenerator(
    rescale=1./255,
    validation_split=0.2,
    rotation_range=25,
    width_shift_range=0.1,
    height_shift_range=0.1,
    shear_range=0.2,
    zoom_range=0.2,
    horizontal_flip=True,
    brightness_range=[0.6, 1.4],
    channel_shift_range=30.0
)

# Инверсированные + шум
datagen_augmented = ImageDataGenerator(
    rescale=1./255,
    validation_split=0.2,
    preprocessing_function=advanced_preprocessing
)

# Генераторы
train_gen_normal = datagen_normal.flow_from_directory(
    DATA_DIR,
    target_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    subset='training'
)

train_gen_augmented = datagen_augmented.flow_from_directory(
    DATA_DIR,
    target_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    subset='training'
)

val_gen = datagen_normal.flow_from_directory(
    DATA_DIR,
    target_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    subset='validation'
)

# 🔀 Объединённый генератор
from tensorflow.keras.utils import Sequence


class CombinedGenerator(Sequence):
    def __init__(self, gen1, gen2):
        self.gen1 = gen1
        self.gen2 = gen2
        self.length = max(len(gen1), len(gen2))

    def __len__(self):
        return self.length

    def __getitem__(self, idx):
        batch1 = self.gen1[idx % len(self.gen1)]
        batch2 = self.gen2[idx % len(self.gen2)]
        x = np.concatenate([batch1[0], batch2[0]], axis=0)
        y = np.concatenate([batch1[1], batch2[1]], axis=0)
        return x, y

train_gen = CombinedGenerator(train_gen_normal, train_gen_augmented)

# 🚀 Компиляция и обучение
print("🚀 Начинаем обучение...")
model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=1e-4),
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

model.fit(train_gen, validation_data=val_gen, epochs=EPOCHS)

# 💾 Сохраняем модель
print("💾 Сохраняем дообученную модель...")
model.save(SAVE_PATH)
print(f"✅ Модель сохранена в: {SAVE_PATH}")
