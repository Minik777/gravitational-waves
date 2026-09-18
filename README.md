# Gravitational Waves Catalog

Дашборд с каталогом гравитационно-волновых событий (слияния чёрных дыр и нейтронных звёзд) на основе открытых данных GWOSC.

## Стек

- **ClickHouse** — колоночная база данных для хранения событий
- **Python** — скрипт загрузки данных из GWOSC API
- **DBeaver** — просмотр данных, SQL-запросы
- **Streamlit** — дашборд с графиками
- **GWOSC GWTC API** — источник данных о гравитационно-волновых событиях

## Запуск

1. Подними ClickHouse:
   ```
   docker run -d \
     --name gw-clickhouse \
     -e CLICKHOUSE_USER=default \
     -e CLICKHOUSE_PASSWORD=clickhouse \
     -e CLICKHOUSE_DB=default \
     -p 8123:8123 \
     -p 9000:9000 \
     --ulimit nofile=262144:262144 \
     clickhouse/clickhouse-server:24.3
   ```
2. `python -m venv .venv && .venv\Scripts\activate` (Windows) или `source .venv/bin/activate` (Mac/Linux)
3. `pip install -r requirements.txt`
4. `python load.py` — загрузить каталог событий в ClickHouse
5. `streamlit run dashboard.py` — открыть дашборд

## Что показывает дашборд

- Общее число событий, количество слияний чёрных дыр (BBH) и нейтронных звёзд (BNS)
- Распределение типов слияний
- Диаграмма рассеяния: масса события vs расстояние до него
- Таблица всех событий с сортировкой по массе
