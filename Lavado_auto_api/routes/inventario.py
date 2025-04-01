from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db, Inventario, Insumo
from sqlalchemy import desc

inventario_bp = Blueprint('inventario', __name__, url_prefix='/inventario')


@inventario_bp.route('/')
def listar():
    """Listar todos los items de inventario"""
    # Obtener parámetros de filtrado
    filtro_insumo = request.args.get('insumo', '')

    # Construir consulta base
    query = Inventario.query.join(Inventario.insumo)

    # Aplicar filtros si se proporcionan
    if filtro_insumo:
        query = query.filter(Insumo.Nombre.ilike(f'%{filtro_insumo}%'))

    # Ordenar y ejecutar consulta
    inventario = query.order_by(Insumo.Nombre).all()

    # Calcular valor total del inventario
    valor_total = sum(item.valor_total for item in inventario)

    return render_template('inventario/listado.html',
                           inventario=inventario,
                           valor_total=valor_total,
                           filtro_insumo=filtro_insumo)


@inventario_bp.route('/registrar', methods=['GET', 'POST'])
def registrar():
    """Registrar un nuevo item de inventario o aumentar el stock"""
    if request.method == 'POST':
        insumo_id = request.form['insumo']
        stock = int(request.form['stock'])
        estado = int(request.form['estado'])

        # Verificar que el insumo exista
        insumo = Insumo.query.get(insumo_id)
        if not insumo:
            flash('❌ El insumo seleccionado no existe', 'danger')
            return render_template('inventario/registro.html',
                                   insumos=Insumo.query.all(),
                                   valores=request.form)

        # Verificar que el stock sea positivo
        if stock <= 0:
            flash('❌ La cantidad debe ser mayor a 0', 'danger')
            return render_template('inventario/registro.html',
                                   insumos=Insumo.query.all(),
                                   valores=request.form)

        # Buscar si ya existe un registro para este insumo
        # Nota: En una implementación real, probablemente querrías un control
        # de lotes de inventario en lugar de sumar al existente
        item_existente = Inventario.query.filter_by(Id_insumo=insumo_id).first()

        if item_existente:
            # Aumentar stock del existente
            item_existente.Stock += stock
            flash('✅ Stock actualizado correctamente', 'success')
        else:
            # Crear nuevo registro
            item = Inventario(
                Id_insumo=insumo_id,
                Stock=stock,
                Estado=estado
            )
            db.session.add(item)
            flash('✅ Item de inventario registrado correctamente', 'success')

        db.session.commit()
        return redirect(url_for('inventario.listar'))

    # Mostrar formulario (GET)
    insumos = Insumo.query.filter_by(Estado='Activo').all()
    return render_template('inventario/registro.html', insumos=insumos)


@inventario_bp.route('/<int:id>/ajustar', methods=['GET', 'POST'])
def ajustar(id):
    """Ajustar la cantidad de un item de inventario"""
    item = Inventario.query.get_or_404(id)

    if request.method == 'POST':
        nuevo_stock = int(request.form['stock'])
        motivo = request.form['motivo']

        # Registrar el ajuste (en un sistema real se guardaría un registro de este ajuste)
        stock_anterior = item.Stock
        item.Stock = nuevo_stock

        # Actualizar estado si es necesario
        if nuevo_stock == 0:
            item.Estado = 0  # Agotado
        else:
            item.Estado = 1  # Disponible

        db.session.commit()

        diferencia = nuevo_stock - stock_anterior
        flash(f'✅ Stock ajustado: {stock_anterior} → {nuevo_stock} (Diferencia: {diferencia})', 'success')

        return redirect(url_for('inventario.listar'))

    return render_template('inventario/ajustar.html', item=item)


@inventario_bp.route('/reporte')
def reporte():
    """Generar un reporte del inventario"""
    # Calcular estadísticas
    inventario = Inventario.query.all()

    total_items = len(inventario)
    valor_total = sum(item.valor_total for item in inventario)
    items_agotados = sum(1 for item in inventario if item.Stock == 0)
    items_criticos = sum(1 for item in inventario if 0 < item.Stock < 10)

    # Calcular valor por tipo de insumo
    valor_por_tipo = {}
    for item in inventario:
        tipo_nombre = item.insumo.tipo_insumo.Nombre
        if tipo_nombre not in valor_por_tipo:
            valor_por_tipo[tipo_nombre] = 0
        valor_por_tipo[tipo_nombre] += item.valor_total

    # Ordenar los tipos por valor
    valor_por_tipo = dict(sorted(valor_por_tipo.items(), key=lambda x: x[1], reverse=True))

    return render_template('inventario/reporte.html',
                           inventario=inventario,
                           total_items=total_items,
                           valor_total=valor_total,
                           items_agotados=items_agotados,
                           items_criticos=items_criticos,
                           valor_por_tipo=valor_por_tipo)