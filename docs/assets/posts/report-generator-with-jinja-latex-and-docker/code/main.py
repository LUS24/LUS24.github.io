import jinja2
from pathlib import Path
from subprocess import call
import seaborn as sns
import matplotlib

# matplotlib configuration
matplotlib.use("pgf")
matplotlib.rcParams.update({
    "pgf.texsystem": "xelatex",
    'font.family': 'serif',
    'text.usetex': True,
    'pgf.rcfonts': False,
})

# Jinja2 configuration
latex_jinja_env = jinja2.Environment(
    block_start_string = '\\BLOCK{',
    block_end_string = '}',
    variable_start_string = '\\VAR{',
    variable_end_string = '}',
    comment_start_string = '\\#{',
    comment_end_string = '}',
    line_statement_prefix = '%%',
    line_comment_prefix = '%#',
    trim_blocks = True,
    autoescape = False,
    lstrip_blocks=True,
    loader = jinja2.FileSystemLoader(Path.cwd().absolute())
)

template = latex_jinja_env.get_template('./templates/main_template.tex')

# Directories configuration
WORKING_DIR = Path.cwd()
OUTPUT_DIR = Path.cwd().joinpath('outputs')
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
PLOT_DIR_PATH = WORKING_DIR.joinpath("assets").joinpath("plots")
PLOT_DIR_PATH.mkdir(parents=True, exist_ok=True)
TEX_FILE_PATH = OUTPUT_DIR.joinpath("main.tex")

# Helper functions
def build_tex(content: dict):
    """
    Renders the content using the Jinja2 template and writes it to a .tex file.
    """
    with open(TEX_FILE_PATH, "w") as f:
        f.write(template.render(content=content))


def build_pdf():
    """
    Runs the xelatex command on the .tex file to generate the pdf file.
    -interaction=batchmode is used to prevent xelatex to ask for user input.
    """
    call(["xelatex", "-interaction=batchmode", TEX_FILE_PATH])


def clean():
    """
    Moves the pdf file to the output directory 
    and removes the other files generated by xelatex.
    """
    file_extensions = ['log', 'pdf', 'aux']
    for file in WORKING_DIR.glob('*'):
        extension = file.suffix.strip('.')
        if extension in file_extensions:
            if extension != 'pdf':
                file.unlink()
            else:
                file.replace(OUTPUT_DIR.joinpath(file.name))


if __name__ == "__main__":
    
    # Load example data
    df = sns.load_dataset('iris')

    content = {
        "title": "Testing Latex with Jinja2 and Pandas",
        "summary": "This is an example of how to use Jinja2 and Pandas to generate a Latex document.",
        "sections": [
            {
                "title": "First Section",
                "body": [
                    {"text": "This is the first section"},
                ]
            },
            {
                "title": "Second Section",
                "body": [
                    {"text": "This is the second section."},
                ]
            },
        ],
    }

    # Adding a table to the content
    content["sections"].append({
        "title": "Data",
        "body": [
            {"text": "Example of pandas table."},
            {"table": df.sample(10).to_latex(
                longtable=True, 
                caption=("Random sample of 10 rows of the Iris dataset loaded from the seaborn Python library", 
                         "Iris Dataset sample."), 
                escape=True)
            },
        ]
    })


    # Adding a plot to the content
    pairplot = sns.pairplot(df, hue='species', height=1.5)
    sns.move_legend(
        pairplot, "lower center",
        bbox_to_anchor=(0.4, 1), 
        ncol=3,
        title=None, 
        frameon=False,
    )

    pairplot.savefig(PLOT_DIR_PATH.joinpath("pairplot.pgf"))


    content["sections"].append({
        "title": "Plot",
        "body": [
            {"text": "Example of seaborn plot."},
            {"figure": {
                "path": PLOT_DIR_PATH.joinpath("pairplot.pgf").relative_to(WORKING_DIR).as_posix(),
                "caption": "Pairplot of the Iris dataset.",
                "label": "fig:pairplot"
            }}
        ]
    })

    build_tex(content)
    build_pdf()
    clean()
