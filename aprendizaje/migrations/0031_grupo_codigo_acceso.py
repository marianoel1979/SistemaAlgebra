from django.db import migrations, models
import secrets

def asignar_codigos(apps, schema_editor):
    Grupo = apps.get_model("aprendizaje", "Grupo")
    usados = set(Grupo.objects.exclude(codigo__isnull=True).values_list("codigo", flat=True))
    for grupo in Grupo.objects.filter(codigo__isnull=True):
        while True:
            codigo = secrets.token_hex(4).upper()
            if codigo not in usados:
                usados.add(codigo)
                break
        grupo.codigo = codigo
        grupo.save(update_fields=["codigo"])

class Migration(migrations.Migration):
    dependencies = [("aprendizaje", "0030_progreso_ejercicios_evaluacion_realizados")]
    operations = [
        migrations.AddField(
            model_name="grupo",
            name="codigo",
            field=models.CharField(max_length=40, unique=True, null=True, blank=True),
        ),
        migrations.RunPython(asignar_codigos, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="grupo",
            name="codigo",
            field=models.CharField(max_length=40, unique=True),
        ),
    ]
