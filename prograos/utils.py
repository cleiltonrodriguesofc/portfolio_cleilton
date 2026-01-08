from decimal import Decimal


class GrainCalculator:
    """
    Classe para realizar cálculos automáticos específicos para soja e milho.
    """

    @staticmethod
    def calcular_peso_util(peso_bruto, umidade, impurezas):
        """
        Calcula o peso útil baseado no peso bruto, umidade e impurezas.

        Args:
            peso_bruto (Decimal): Peso bruto da amostra
            umidade (Decimal): Percentual de umidade
            impurezas (Decimal): Percentual de impurezas

        Returns:
            Decimal: Peso útil calculado
        """
        if not all([peso_bruto, umidade, impurezas]):
            return None

        # Fórmula: Peso Útil = Peso Bruto * (1 - umidade/100) * (1 - impurezas/100)
        fator_umidade = 1 - (umidade / 100)
        fator_impurezas = 1 - (impurezas / 100)
        peso_util = peso_bruto * fator_umidade * fator_impurezas

        return peso_util.quantize(Decimal('0.001'))

    @staticmethod
    def calcular_classificacao_soja(umidade, impurezas):
        """
        Classifica a soja baseada nos parâmetros de umidade e impurezas.

        Args:
            umidade (Decimal): Percentual de umidade
            impurezas (Decimal): Percentual de impurezas

        Returns:
            str: Status da classificação (ACEITA, REJEITADA, PENDENTE)
        """
        if umidade is None or impurezas is None:
            return 'PENDENTE'

        # Critérios para soja (valores exemplo - ajustar conforme necessário)
        if umidade <= 14 and impurezas <= 1:
            return 'ACEITA'
        elif umidade > 18 or impurezas > 3:
            return 'REJEITADA'
        else:
            return 'PENDENTE'

    @staticmethod
    def calcular_classificacao_milho(umidade, impurezas):
        """
        Classifica o milho baseado nos parâmetros de umidade e impurezas.

        Args:
            umidade (Decimal): Percentual de umidade
            impurezas (Decimal): Percentual de impurezas

        Returns:
            str: Status da classificação (ACEITA, REJEITADA, PENDENTE)
        """
        if umidade is None or impurezas is None:
            return 'PENDENTE'

        # Critérios para milho (valores exemplo - ajustar conforme necessário)
        if umidade <= 15 and impurezas <= 1.5:
            return 'ACEITA'
        elif umidade > 20 or impurezas > 4:
            return 'REJEITADA'
        else:
            return 'PENDENTE'

    @staticmethod
    def aplicar_calculos(amostra):
        """
        Aplica todos os cálculos automáticos para uma amostra.

        Args:
            amostra: Instância do modelo Amostra

        Returns:
            dict: Dicionário com os valores calculados
        """
        resultado = {}

        # Calcular peso útil
        peso_util = GrainCalculator.calcular_peso_util(
            amostra.peso_bruto,
            amostra.umidade,
            amostra.impurezas
        )
        resultado['peso_util'] = peso_util

        # Calcular classificação baseada no tipo de grão
        if amostra.tipo_grao == 'SOJA':
            status = GrainCalculator.calcular_classificacao_soja(
                amostra.umidade,
                amostra.impurezas
            )
        elif amostra.tipo_grao == 'MILHO':
            status = GrainCalculator.calcular_classificacao_milho(
                amostra.umidade,
                amostra.impurezas
            )
        else:
            status = 'PENDENTE'

        resultado['status'] = status

        return resultado
