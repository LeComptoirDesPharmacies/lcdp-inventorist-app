import array

from api.consume.gen.factory.models.assembly_status import AssemblyStatus
from api.consume.gen.factory.models.assembly import Assembly

def fromAssembliesToTable(assemblies: array):
    result = []
    for assembly in assemblies.records if assemblies else []:
        result.append(fromAssemblyToTable(assembly))

    return result

def computePercent(successful_steps: int, failed_steps: int, total_steps: int) -> int:
    if total_steps is None or total_steps == 0:
        return 0
    cursor = successful_steps + failed_steps
    return round((cursor / total_steps) * 100)

def fromAssemblyTypeToString(factory_type : str) -> str:
    if factory_type == 'PRODUCT_UPSERT':
        return 'Import produit'
    if factory_type == 'SALE_OFFER_UPSERT':
        return 'Import annonce'
    if factory_type == 'OFFER_PLANIFICATION':
        return 'Import offre'
    return factory_type

def fromAssemblyStatusToString(status: str) -> str:
    if status == AssemblyStatus.PENDING:
        return 'En attente'
    if status == AssemblyStatus.PREPROCESSING:
        return 'Pré traitement'
    if status == AssemblyStatus.PROCESSING:
        return 'Traitement en cours'
    if status == AssemblyStatus.POSTPROCESSING:
        return 'Post traitement'
    if status == AssemblyStatus.PREPROCESSING_FAILED:
        return 'Erreur au pré traitement'
    if status == AssemblyStatus.PROCESSING_FAILED:
        return 'Erreur pendant le traitement'
    if status == AssemblyStatus.POSTPROCESSING_FAILED:
        return 'Erreur en post traitement'
    if status == AssemblyStatus.DONE:
        return 'Terminé'
    return status

def get_action(assembly: Assembly) -> str:
    if assembly.status == AssemblyStatus.DONE:
        return assembly.output.href
    return ' '

def fromAssemblyToTable(assembly: Assembly) -> dict:
    res = dict({
        'id' : assembly.id,
        'created_at': assembly.created_at.strftime("%m/%d/%Y, %H:%M:%S"),
        'type': fromAssemblyTypeToString(assembly.factory_type.type),
        'status': fromAssemblyStatusToString(assembly.status),
        'percent': "{} %".format(computePercent(assembly.successful_steps, assembly.failed_steps, assembly.total_steps)),
        'action': get_action(assembly),
        'assembly': assembly,
        'statusType': assembly.status
    })

    return res