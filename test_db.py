import asyncio
import asyncpg

async def test():
    for port in [5432, 5433]:
        for password in ['postgres', '', '1234', 'admin']:
            try:
                conn = await asyncpg.connect(
                    host='localhost',
                    port=port,
                    database='automarket',
                    user='postgres',
                    password=password
                )
                print(f'✅ Подключение успешно! Порт: {port}, Пароль: "{password}"')
                await conn.close()
                return
            except Exception as e:
                print(f'❌ Порт {port}, пароль "{password}": {e}')

asyncio.run(test())