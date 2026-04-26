import sqlite3

conexao = sqlite3.connect('banco.db')

cursor = conexao.cursor()

cursor.execute('DROP TABLE _alembic_tmp_emprestimo')
conexao.commit()