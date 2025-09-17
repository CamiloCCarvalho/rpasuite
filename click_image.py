# ./utils/close_app.py


# Third-party imports
import time
from pathlib import Path
from typing import Optional, Tuple, Union

import pyautogui


# pylint: disable=import-outside-toplevel
def check_opencv_availability() -> bool:
    """Verifica se OpenCV está disponível no sistema."""
    try:
        # pylint: disable=import-outside-toplevel
        import cv2  # pylint: disable=unused-import

        return True
    except ImportError:
        return False


OPENCV_AVAILABLE = check_opencv_availability()

if OPENCV_AVAILABLE:
    print("OpenCV detectado - funcionalidade de confidence habilitada")
else:
    print("OpenCV não encontrado - confidence será ignorado. Para melhor precisão, instale: pip install opencv-python")


# Configurações globais do PyAutoGUI
pyautogui.FAILSAFE = True  # Move o mouse para canto superior esquerdo para parar
pyautogui.PAUSE = 0.1  # Pausa padrão entre comandos


class ImageClickError(Exception):
    """Exceção customizada para erros de clique em imagem."""


def click_image(
    image_label: str,
    images_folder: Union[str, Path] = "resource",
    confidence: float = 0.78,
    timeout: float = 10.0,
    click_center: bool = True,
    click_button: str = "left",
    double_click: bool = False,
    search_interval: float = 0.5,
    region: Optional[Tuple[int, int, int, int]] = None,
    grayscale: bool = True,
    display_details: bool = False,
) -> Union[Tuple[int, int], bool]:
    """
    Localiza uma imagem na tela e clica nela.

    Esta função busca por uma imagem específica na tela usando PyAutoGUI
    e realiza um clique na posição encontrada. Implementa busca com timeout
    e diferentes níveis de confiança para melhor precisão (quando OpenCV disponível).

    Args:
        image_label (str): Nome do arquivo de imagem (com ou sem extensão).
                          Ex: 'botao_ok' ou 'botao_ok.png'
        images_folder (Union[str, Path], optional): Caminho para pasta das imagens.
                                                   Default: "images"
        confidence (float, optional): Nível de confiança para localização (0.0-1.0).
                                    Requer OpenCV instalado. Se não disponível, será ignorado.
                                    Valores altos = maior precisão, menor tolerância.
                                    Default: 0.8
        timeout (float, optional): Tempo limite em segundos para busca.
                                  Default: 10.0
        click_center (bool, optional): Se True, clica no centro da imagem.
                                     Se False, clica no canto superior esquerdo.
                                     Default: True
        click_button (str, optional): Botão do mouse ('left', 'right', 'middle').
                                    Default: 'left'
        double_click (bool, optional): Se True, realiza duplo clique.
                                     Default: False
        search_interval (float, optional): Intervalo entre tentativas de busca.
                                         Default: 0.5 segundos
        region (Optional[Tuple[int, int, int, int]], optional): Região da tela para buscar.
                                                               Formato: (x, y, largura, altura)
                                                               Default: None (tela inteira)
        grayscale (bool, optional): Se True, busca em escala de cinza (mais rápido).
                                  Default: True
        display_details (bool, optional): Se True, exibe detalhes.
                                  Default: False

    Returns:
        Union[Tuple[int, int], bool]: Coordenadas (x, y) do centro da imagem se encontrada
                                     ou False se não encontrada dentro do timeout.

    Raises:
        ImageClickError: Se houver erro na configuração ou execução.
        FileNotFoundError: Se o arquivo de imagem não for encontrado.
        ValueError: Se os parâmetros estiverem inválidos.

    Note:
        Para usar o parâmetro confidence, instale o OpenCV: pip install opencv-python
        Sem OpenCV, a função funcionará com busca exata de pixels.

    Example:
        >>> # Busca e clica em um botão
        >>> position = click_image('botao_salvar.png', confidence=0.9, timeout=5.0)
        >>> if position:
        ...     print(f"Clicou na posição: {position}")
        ... else:
        ...     print("Imagem não encontrada")

        >>> # Busca em região específica da tela
        >>> region_resultado = click_image(
        ...     'icone_menu',
        ...     region=(0, 0, 500, 300),  # Busca apenas no canto superior esquerdo
        ...     confidence=0.7
        ... )
    """

    # Validação de parâmetros
    _validate_parameters(confidence, timeout, search_interval, click_button, region)

    # Resolve o caminho completo da imagem
    image_path = _resolve_image_path(image_label, images_folder)

    # Aviso se confidence será ignorado
    if confidence != 0.8 and not OPENCV_AVAILABLE:
        print(f"Parâmetro confidence={confidence} será ignorado. " + "Instale OpenCV: pip install opencv-python")

    print(f"Iniciando busca por imagem: {image_path}")
    if display_details:
        print(
            f"Configurações: confidence={'N/A' if not OPENCV_AVAILABLE else confidence}, "
            + f"timeout={timeout}s, region={region}"
        )

    # Configurações temporárias do PyAutoGUI
    original_pause = pyautogui.PAUSE
    pyautogui.PAUSE = 0.05  # Reduz pausa para busca mais rápida

    try:
        # Executa a busca com timeout
        position = _search_image_with_timeout(
            image_path=image_path,
            confidence=confidence,
            timeout=timeout,
            search_interval=search_interval,
            region=region,
            grayscale=grayscale,
        )

        if not position:
            print(f"Imagem não encontrada após {timeout}s: {image_path.name}")
            return False

        # Calcula posição do clique
        click_position = _calculate_click_position(position, click_center)

        # Realiza o clique
        _perform_click(click_position, click_button, double_click)

        # print(f"Clique realizado!")
        return click_position

    except Exception as e:
        error_msg = f"Erro ao processar clique em imagem {image_path.name}: {str(e)}"
        print(error_msg)
        raise ImageClickError(error_msg) from e

    finally:
        # Restaura configuração original
        pyautogui.PAUSE = original_pause


def find_image_position(
    image_label: str,
    images_folder: Union[str, Path] = "resource",
    confidence: float = 0.8,
    timeout: float = 5.0,
    region: Optional[Tuple[int, int, int, int]] = None,
    grayscale: bool = False,
) -> Union[Tuple[int, int], bool]:
    """
    Encontra a posição de uma imagem na tela sem clicar.

    Função utilitária para apenas localizar uma imagem sem realizar clique.
    Útil para verificar presença de elementos ou obter coordenadas.

    Args:
        image_label (str): Nome do arquivo de imagem.
        images_folder (Union[str, Path], optional): Pasta das imagens. Default: "images"
        confidence (float, optional): Nível de confiança. Default: 0.8
        timeout (float, optional): Timeout em segundos. Default: 5.0
        region (Optional[Tuple], optional): Região de busca. Default: None
        grayscale (bool, optional): Busca em escala de cinza. Default: False

    Returns:
        Union[Tuple[int, int], bool]: Coordenadas do centro da imagem ou False.
    """

    _validate_parameters(confidence, timeout, 0.5, "left", region)
    image_path = _resolve_image_path(image_label, images_folder)

    try:
        position = _search_image_with_timeout(
            image_path=image_path,
            confidence=confidence,
            timeout=timeout,
            search_interval=0.5,
            region=region,
            grayscale=grayscale,
        )

        if position:
            return _calculate_click_position(position, click_center=True)
        return False

    except Exception as e:
        print(f"Erro ao buscar imagem {image_path.name}: {e}")
        return False


def _validate_parameters(
    confidence: float,
    timeout: float,
    search_interval: float,
    click_button: str,
    region: Optional[Tuple[int, int, int, int]],
) -> None:
    """Valida os parâmetros de entrada da função."""

    if not 0.0 <= confidence <= 1.0:
        raise ValueError(f"Confidence deve estar entre 0.0 e 1.0, recebido: {confidence}")

    if timeout <= 0:
        raise ValueError(f"Timeout deve ser positivo, recebido: {timeout}")

    if search_interval <= 0:
        raise ValueError(f"Search interval deve ser positivo, recebido: {search_interval}")

    if click_button not in ["left", "right", "middle"]:
        raise ValueError(f"Click button deve ser 'left', 'right' ou 'middle', recebido: {click_button}")

    if region is not None:
        if not isinstance(region, (tuple, list)) or len(region) != 4:
            raise ValueError("Region deve ser uma tupla com 4 elementos: (x, y, largura, altura)")

        if any(not isinstance(val, int) or val < 0 for val in region):
            raise ValueError("Todos os valores de region devem ser inteiros não-negativos")


def _resolve_image_path(image_label: str, images_folder: Union[str, Path]) -> Path:
    """Resolve o caminho completo para o arquivo de imagem."""

    folder_path = Path(images_folder)

    # Se image_label já tem extensão, usa diretamente
    if "." in image_label:
        image_path = folder_path / image_label
    else:
        # Tenta diferentes extensões comuns
        extensions = [".png", ".jpg", ".jpeg", ".bmp", ".gif"]
        image_path = None

        for ext in extensions:
            candidate = folder_path / f"{image_label}{ext}"
            if candidate.exists():
                image_path = candidate
                break

        if not image_path:
            # Se não encontrou, usa .png como padrão para erro mais claro
            image_path = folder_path / f"{image_label}.png"

    if not image_path.exists():
        raise FileNotFoundError(f"Arquivo de imagem não encontrado: {image_path}")

    return image_path


def _search_image_with_timeout(
    image_path: Path,
    confidence: float,
    timeout: float,
    search_interval: float,
    region: Optional[Tuple[int, int, int, int]],
    grayscale: bool,
) -> Optional[any]:
    """Busca por imagem na tela com timeout, considerando disponibilidade do OpenCV."""

    start_time = time.time()
    attempts = 0

    while time.time() - start_time < timeout:
        attempts += 1

        try:
            # Monta argumentos para locateOnScreen baseado na disponibilidade do OpenCV
            locate_args = {"image": str(image_path), "region": region, "grayscale": grayscale}

            # Adiciona confidence apenas se OpenCV estiver disponível
            if OPENCV_AVAILABLE:
                locate_args["confidence"] = confidence

            # Busca a imagem na tela
            location = pyautogui.locateOnScreen(**locate_args)

            if location:
                print(f"Imagem encontrada na tentativa {attempts}.")
                return location

        except pyautogui.ImageNotFoundException:
            # Imagem não encontrada nesta tentativa
            pass
        except TypeError as e:
            if "confidence" in str(e):
                # Fallback caso ainda ocorra erro com confidence
                print("Erro com confidence detectado, tentando sem o parâmetro...")
                try:
                    location = pyautogui.locateOnScreen(str(image_path), region=region, grayscale=grayscale)
                    if location:
                        print(f"Imagem encontrada na tentativa {attempts} (sem confidence): {location}")
                        return location
                except Exception as error:
                    print(f"falha na tentativa sem confidence: {error}.")
            else:
                print(f"Erro durante busca da imagem (tentativa {attempts}): {e}")
        except Exception as e:
            print(f"Erro durante busca da imagem (tentativa {attempts}): {e}")

        # Aguarda antes da próxima tentativa
        if time.time() - start_time < timeout:
            time.sleep(search_interval)

    print(f"Busca finalizada após {attempts} tentativas em {timeout}s")
    return None


def _calculate_click_position(image_box: any, click_center: bool) -> Tuple[int, int]:
    """Calcula a posição exata do clique baseada na localização da imagem."""

    if click_center:
        # Clica no centro da imagem
        center_x = image_box.left + image_box.width // 2
        center_y = image_box.top + image_box.height // 2
        return (center_x, center_y)
    # Clica no canto superior esquerdo
    return (image_box.left, image_box.top)


def _perform_click(position: Tuple[int, int], click_button: str, double_click: bool) -> None:
    """Realiza o clique na posição especificada."""

    x, y = position

    # Move o mouse para a posição (opcional, mas ajuda na visualização)
    pyautogui.moveTo(x, y, duration=0.1)

    # Realiza o clique
    if double_click:
        pyautogui.doubleClick(x, y, button=click_button)
        print(f"Duplo clique realizado em ({x}, {y}) com botão {click_button}")
    else:
        pyautogui.click(x, y, button=click_button)
        print(f"Clique realizado em ({x}, {y}) com botão {click_button}")


# Funções de conveniência para casos específicos
def wait_and_click(
    image_label: str, images_folder: Union[str, Path] = "resource", confidence: float = 0.8, timeout: float = 30.0
) -> Union[Tuple[int, int], bool]:
    """
    Aguarda uma imagem aparecer na tela e clica nela.

    Função de conveniência para aguardar elementos que podem demorar para aparecer.
    """
    return click_image(
        image_label=image_label,
        images_folder=images_folder,
        confidence=confidence,
        timeout=timeout,
        search_interval=1.0,  # Intervalo maior para aguardar
    )


def quick_click(image_label: str, images_folder: Union[str, Path] = "resource") -> Union[Tuple[int, int], bool]:
    """
    Clique rápido com configurações padrão otimizadas.

    Função de conveniência para cliques rápidos com configurações balanceadas.
    """
    return click_image(
        image_label=image_label,
        images_folder=images_folder,
        confidence=0.8,
        timeout=3.0,
        search_interval=0.2,
        grayscale=True,  # Mais rápido
    )
