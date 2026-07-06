from django.db import migrations, models


def forwards(apps, schema_editor):
    schema_editor.execute(
        "ALTER TABLE hotel_faixaprecocategoria ADD COLUMN qtd_hospedes INT UNSIGNED NOT NULL DEFAULT 1"
    )
    schema_editor.execute(
        "UPDATE hotel_faixaprecocategoria SET qtd_hospedes = qtd_hospedes_min"
    )
    schema_editor.execute(
        "ALTER TABLE hotel_faixaprecocategoria DROP COLUMN qtd_hospedes_min"
    )
    schema_editor.execute(
        "ALTER TABLE hotel_faixaprecocategoria DROP COLUMN qtd_hospedes_max"
    )


class Migration(migrations.Migration):

    dependencies = [
        ('hotel', '0005_hospedagem_quantidade_hospedes_and_more'),
    ]

    operations = [
        migrations.RunPython(forwards, migrations.RunPython.noop),
    ]

    atomic = False
