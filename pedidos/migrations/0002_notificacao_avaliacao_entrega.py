from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('pedidos', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='pedido',
            name='entrega_confirmada',
            field=models.BooleanField(default=False, verbose_name='Entrega Confirmada pelo Produtor'),
        ),
        migrations.CreateModel(
            name='Notificacao',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo', models.CharField(choices=[('STATUS_ATUALIZADO', 'Status Atualizado'), ('ENTREGUE', 'Pedido Entregue - Confirmar'), ('AVALIACAO', 'Avaliação Recebida')], default='STATUS_ATUALIZADO', max_length=30, verbose_name='Tipo')),
                ('mensagem', models.TextField(verbose_name='Mensagem')),
                ('lida', models.BooleanField(default=False, verbose_name='Lida')),
                ('data_criacao', models.DateTimeField(auto_now_add=True)),
                ('destinatario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notificacoes', to=settings.AUTH_USER_MODEL, verbose_name='Destinatário')),
                ('pedido', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notificacoes', to='pedidos.pedido', verbose_name='Pedido')),
            ],
            options={
                'verbose_name': 'Notificação',
                'verbose_name_plural': 'Notificações',
                'ordering': ['-data_criacao'],
            },
        ),
        migrations.CreateModel(
            name='AvaliacaoProduto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nota', models.PositiveSmallIntegerField(choices=[(1, '1 estrela'), (2, '2 estrelas'), (3, '3 estrelas'), (4, '4 estrelas'), (5, '5 estrelas')], verbose_name='Nota')),
                ('comentario', models.TextField(blank=True, verbose_name='Comentário')),
                ('data_criacao', models.DateTimeField(auto_now_add=True)),
                ('avaliador', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='avaliacoes_feitas', to=settings.AUTH_USER_MODEL, verbose_name='Avaliador')),
                ('pedido', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='avaliacoes', to='pedidos.pedido', verbose_name='Pedido')),
                ('produto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='avaliacoes', to='produtos.produto', verbose_name='Produto')),
            ],
            options={
                'verbose_name': 'Avaliação',
                'verbose_name_plural': 'Avaliações',
                'ordering': ['-data_criacao'],
            },
        ),
        migrations.AddConstraint(
            model_name='avaliacaoproduto',
            constraint=models.UniqueConstraint(fields=['pedido', 'produto', 'avaliador'], name='unique_avaliacao_por_pedido_produto'),
        ),
    ]
