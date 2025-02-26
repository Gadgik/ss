import streamlit as st
import pandas as pd
import pickle
from sklearn.metrics.pairwise import cosine_similarity

# Загрузка модели
text_vectors = pickle.load(open('/mnt/d/data/text_vectors.pkl', 'rb'))
vectorizer = pickle.load(open('/mnt/d/data/vectorizer.pkl', 'rb'))
df = pd.read_csv('/mnt/d/data/df.csv')

# Функция предсказания
def model(request):
    request_vector = vectorizer.transform([request])
    similarities = cosine_similarity(request_vector, text_vectors)
    recommended_indexes = similarities.argsort()[0][-3:][::-1]  # Топ-3 рекомендаций
    rec = [df.iloc[idx]['name'] for idx in recommended_indexes]
    return rec

# Создание интерфейса Streamlit
st.title("Рекомендация отелей")

# Инструкция
st.markdown("""
### Инструкция:
1. Введите текст в поле ниже.
2. Нажмите кнопку "Предсказать".
3. Результат предсказания для всех отелей появится сразу ниже.
4. Вы можете очистить ввод и попробовать снова.
""")

# Ввод текста
user_input = st.text_area("Введите запрос:", "")

# Кнопка предсказания
if st.button("Предсказать"):
    st.empty()
    if user_input:
        prediction = model(user_input)

        st.write("Рекомендуемые отели:")
        for i, hotel in enumerate(prediction):
            st.write(f"{i+1}: {hotel}")
    else:
        st.warning("Пожалуйста, введите текст.")

