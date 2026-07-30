from django.db import migrations, models


def forwards(apps, schema_editor):
    with schema_editor.connection.cursor() as cursor:
        cursor.execute("SHOW COLUMNS FROM hotel_faixaprecocategoria LIKE 'qtd_hospedes'")
        col_existe = cursor.fetchone()

        if not col_existe:
            cursor.execute(
                "ALTER TABLE hotel_faixaprecocategoria ADD COLUMN qtd_hospedes INT UNSIGNED NOT NULL DEFAULT 1"
            )
            cursor.execute(
                "UPDATE hotel_faixaprecocategoria SET qtd_hospedes = qtd_hospedes_min"
            )

        cursor.execute("SHOW COLUMNS FROM hotel_faixaprecocategoria LIKE 'qtd_hospedes_min'")
        col_antigo_min = cursor.fetchone()
        if col_antigo_min:
            cursor.execute("ALTER TABLE hotel_faixaprecocategoria DROP COLUMN qtd_hospedes_min")

        cursor.execute("SHOW COLUMNS FROM hotel_faixaprecocategoria LIKE 'qtd_hospedes_max'")
        col_antigo_max = cursor.fetchone()
        if col_antigo_max:
            cursor.execute("ALTER TABLE hotel_faixaprecocategoria DROP COLUMN qtd_hospedes_max")


class Migration(migrations.Migration):

    dependencies = [
        ('hotel', '0005_hospedagem_quantidade_hospedes_and_more'),
    ]

    operations = [
        migrations.RunPython(forwards, migrations.RunPython.noop),
    ]

    atomic = False
