---
title: Generating reports with Jinja, LaTeX and Docker
date: 2024-03-20
authors:
  - leonardo
categories:
  - Python
  - Latex
  - Jinja2
  - Docker
  - Reports
  - Pandas
comments: true
donations: true
---


# Generating reports with Jinja, LaTeX and Docker

Sharing information is a key aspect in most human activities and where reports play a role. Reports serve various purposes such as tracking our children's development at school, seeing our credit card expenses, evaluating statistics after training a machine learning model and the list goes on.

In certain situations, there is a need to generate many reports that look similar which can be a tedious task if performed manually. In this blog post I will show how to generate reports programmatically using a Python template engine called [Jinja](https://jinja.palletsprojects.com), a high-quality document preparation system called [Latex](https://www.latex-project.org/) and a platform called [Docker](https://docs.docker.com/get-started/overview/) used to create applications in loosely isolated environments.

<!-- more -->


## Requirements

The requirements list is short for this one, only docker is needed because all the code will run inside what is called a docker container, [click here for extra information about how to install Docker](https://docs.docker.com/get-docker/).

## Customizing a Docker image

To learn what an image is we can go the [Docker documentation](https://docs.docker.com/get-started/overview/#images):

> *An image is a read-only template with instructions for creating a Docker container. Often, an image is based on another image, with some additional customization..."*

To customize an image we use a [Dockerfile](https://docs.docker.com/reference/dockerfile/):

>  *"...A Dockerfile is a text document that contains all the commands a user could call on the command line to assemble an image..."*

Ok! Now we know that we need an image to create a container and to customize an image we use a Dockerfile. 

To create a Dockerfile, open a new empty directory and add a new file called... you guess it! `Dockerfile` (with no extension). Then add the following contents:

```dockerfile title="Dockerfile"
FROM python:3.12-alpine3.19

RUN apk update && apk add texmf-dist texlive-full

WORKDIR /code

COPY requirements.txt /code/requirements.txt

RUN pip install -r requirements.txt

COPY . /code/

ENTRYPOINT ["python3", "main.py" ]
```

Let's break each line:

- `FROM python:3.12-alpine3.19`: as the Docker docs mentioned, an image is usually based on another image. This line does exactly that. The [`FROM` instruction](https://docs.docker.com/reference/dockerfile/#from) is used to indicate that we want to use the `python` image with the tag `3.12-alpine3.19`. Which in turn it means that we want Python version 3.12 running on the Alpine Linux version 3.19 operating system.
- `RUN apk update && apk add texmf-dist texlive-full`: this lines uses the [`RUN` instruction](https://docs.docker.com/reference/dockerfile/#run) to add a new layer when building the image that executes a command that updates the references of the package repository and then installs a (La)Tex distribution called [Texlive](https://www.tug.org/texlive/) with all available tex packages.
- `WORKDIR /code`: the [`WORKDIR` instruction](https://docs.docker.com/reference/dockerfile/#workdir) indicates the working directory inside the image during build time.
- `COPY requirements.txt /code/requirements.txt`: we use the [`COPY` instruction](https://docs.docker.com/reference/dockerfile/#copy) to get the `requirements.txt` from the host computer into the docker image.
- `RUN pip install -r requirements.txt`: adds a new layer when building the image that installs the python dependencies.
- `COPY . /code/`: the rest of the files are copied into the image.
- `ENTRYPOINT ["python3", "main.py" ]`: finally, we use the [`ENTRYPOINT` instruction](https://docs.docker.com/reference/dockerfile/#entrypoint) to run the `main.py` file.

Now that the Dockerfile is set, we can continue by adding the files that are going to be included inside the image.

!!! info "Extra information"
    - [Difference between Tex and Latex](https://tex.stackexchange.com/questions/245982/differences-between-texlive-packages-in-linux)
    - [Differences between texlive packages in Linux](https://tex.stackexchange.com/questions/245982/differences-between-texlive-packages-in-linux)


## Adding the requirements

In the current directory, next to the Dockerfile, create a `requirements.txt` file with the following contents:

```txt title="requirements.txt"
Jinja2
matplotlib
seaborn
pandas

```

We will use Jinja2 to render templates, Pandas for working with example data, and Matplotlib and Seaborn to create example plots. Docker will install the packages when we build the image. 

As a next step let us work on the `main.py` file


## Importing the required libraries

At the top of the file add the following imports:

```python title="main.py"
import jinja2
from pathlib import Path
from subprocess import call
import seaborn as sns
import matplotlib
```

Jinja2, Seaborn and Matplotlib are external libraries that we have mentioned before. The built-in python module `pathlib` is a used to work with the filesystem, in particular, the `Path` class is used to represent a system path as python class. The class function from the  `subprocess` built-in python module is used to run commands in the terminal. 


## Configuring plots

To generate plots and figures that look really good, Latex uses the [pgf language](https://en.wikipedia.org/wiki/PGF/TikZ) to specify vector graphics, to enable the backend that supports that language in matplotlib we have to add the following configuration:

```python title="main.py"
matplotlib.use("pgf")
matplotlib.rcParams.update({
    "pgf.texsystem": "xelatex",
    'font.family': 'serif',
    'text.usetex': True,
    'pgf.rcfonts': False,
})
```

!!! info "Matplotlib configuration"
    For extra configuration details check the [matplotlib docs](https://matplotlib.org/stable/users/explain/text/pgf.html).


## Configuring Jinja2

As a templating language, Jinja uses some specific characters to indicate where to inject text, some of those characters overlap with Latex syntax, that is why we need to add some extra configuration:

```python title="main.py"
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
```

In the code above we pass the configuration parameters to the `jinja2.Environment` class constructor and then we specify the template that we want to use, the `main_template.tex` file, which will be [presented below](#the-jinja-template).

!!! info "Jinja2 Environment documentation"
    For extra details about what each parameter check the [Jinja2 reference in the docs](https://jinja.palletsprojects.com/en/3.0.x/api/?highlight=block_start_string#jinja2.Environment). 


## Abstracting the report structure

Before going any further, it is essential to decide how to represent the report contents as code so it can be added systematically. To avoid adding extra complexity, I will use a python dictionaries, but keep in mind that the built-in module [`dataclasses`](https://docs.python.org/3/library/dataclasses.html), or external libraries like [Pydantic](https://docs.pydantic.dev/latest/) can be used to achieve the same.

I will store the dictionary in a variable called `content`. The content will have a title, a summary, and one or more sections. In turn, each section will contain a title and a body. The body will be comprised of parts with of one of the following types: "text", "table", "figure". 

Here is how it will look like:

```python
content = {
    "title": "Some title",
    "summary": "A summary",
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
                {"table": "<table in latex format>"},
                {"figure": {
                    "path": "<posix path to the image file>",
                    "caption": "Some caption",
                    "label": "fig:pairplot"
                    }
                }
            ]
        },
    ],
}
```


## The Jinja template

Now that we have an idea of how the report contents look like in Python code, I will show how it can be rendered systematically using the Jinja syntax. Here is how the template looks like:

```latex title="main_template.tex"
\documentclass[12pt, a4paper]{article}
\usepackage[left=2cm,top=2cm,right=2cm,bottom=2cm,bindingoffset=0cm]{geometry}
\usepackage{graphicx}
\usepackage{booktabs}
\usepackage{longtable}
\usepackage{tikz}
\usepackage{tikz-cd}
\usepackage{pgfplots}

\begin{document}

\title{\VAR{content.title}}

\maketitle

\section{Summary}
\VAR{content.summary}

\BLOCK{ for section in content.sections }
\section{\VAR{ section.title }}
\BLOCK{ for part in section.body }
\VAR{ part.text }

\BLOCK{ if part.table }
\VAR{ part.table }
\BLOCK{ endif }

\BLOCK{ if part.figure }
\begin{figure}
  \begin{center}
      \input{\VAR{part.figure.path}}
  \end{center}
  \caption{\VAR{part.figure.caption}}
\end{figure}
\BLOCK{ endif }

\BLOCK{ endfor }
\BLOCK{ endfor }

\end{document}

```

Lines 1 to 10 are pure Latex code, the first line configures the pages lines 2 to 8 import the required packages to be able to use images, render tables, and create plots. Line 10, `\begin{document}` starts the body of the document.

Next, in line 12 we have the line that contains the first Jinja2 syntax: `\title{\VAR{content.title}}`, the `\title{}` part is Latex and `\VAR{}` indicates the that we want to use a variable with the value `content.title` that comes from Python (check the `variable_start_string` in the [Configuring Jinja2 section](#configuring-jinja2)).

Looking a few lines below, we stumble with the first`\BLOCK` string where it says `\BLOCK{ for section in content.sections }`. In this line we use a for loop to iterate over each section of the `content.sections` variable.

In the next `\BLOCK` a nested for loop is initiated to render each part of the section body. Then we conditionally render tables and figures using if statements with the following structure:

```latex
\BLOCK{ if <some condition> }
Some content
\BLOCK{ endif }
```

Finally, the for loops are ended by doing `\BLOCK{ endfor }` (one for each loop) and then the latex code `\end{document}` is used to finish the document.

!!! info "Latex packages"
    You can get extra information about each latex package in the [Comprehensive Tex Archive Network (CTAN) site](https://ctan.org/).


## Configuring the directories

Going back to the `main.py` file, let's add some directory structure configuration. The `WORKDING_DIR` variable will reference a Path object where the `main.py` file is located, the `OUTPUT_DIR` a reference to the outputs directory, the `PLOT_DIR_PATH` to store the generated plots that will be added to the report, and finally the `TEX_FILE_PATH` which is a reference to the tex file that will be generated from the template. Feel free to adapt the directory structure to your specific project.

```python title="main.py"
# Directories configuration
WORKING_DIR = Path.cwd()
OUTPUT_DIR = Path.cwd().joinpath('outputs')
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
PLOT_DIR_PATH = WORKING_DIR.joinpath("assets").joinpath("plots")
PLOT_DIR_PATH.mkdir(parents=True, exist_ok=True)
TEX_FILE_PATH = OUTPUT_DIR.joinpath("main.tex")
```


## Defining some helper functions

Next, I will define some functions to assist on the task of creating the pdf. Check the [docstrings](https://peps.python.org/pep-0257/#what-is-a-docstring) for details about each function.

```python title="main.py"
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
```

## The main program

After finishing the setup and defining the functions we can proceed to put all together to generate the report. In the same file, let's create an if block that looks like this:

```python title="main.py"
if __name__ == "__main__":
    ...

```

This block will run only if we execute the file as a Python script, for example:

```bash
python main.py
```

[Check this excellent article](https://realpython.com/if-name-main-python/) about `if __name__ == "__main__"` from Real Python for extra information.

- **Loading example data**: With this single line we will load some example data from the Seaborn package and store it in the `df` variable.

```python title="main.py"
df = sns.load_dataset('iris')
```

- **Adding sections**: next, I'll create a variable called `content` and start adding some sections with the structure [presented before](#abstracting-the-report-structure):

```python title="main.py"
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
```

- **Adding tables**: here is an example of how to add a table. We will take advantage of the [`to_latex`](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.to_latex.html) Pandas method to facilitate converting the pandas `dataframe` to Latex in an easy manner.

```python title="main.py"
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
```

- **Adding plots**: in this step I create a new Seaborn pairplot and store it in the `pariplot` variable. Then, I customize the plot, use the `savefig` method to save a the plot in the `pgf` format ready to be loaded by Latex. Finally, the plot is added as a new section of the `content` dictionary.


```python title="main.py"
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
```

- **Using the helper functions**: once all the sections are added I called the `build_text` function passing the `content` variable, with all the sections and metadata, as argument. That function will populate the [Jinja template we fined](#the-jinja-template) to create the `tex` file. Then the `build_pdf` function will create the new `pdf` file using the newly populated `tex` file and lastly, I called the `clean` function to remove unnecessary files and move the output files to the correct directories.

```python
    build_tex(content)
    build_pdf()
    clean()

```


## Putting it all together

Before moving forward on creating the Docker image, confirm that your directory structure looks like this:

```text
├── templates
│   └── main_template.tex
├── Dockerfile
├── main.py
└── requirements.txt
```

Also, check that the contents of the `main.py` file are the following:

```python title="main.py"
--8<-- "docs\assets\posts\report-generator-with-jinja-latex-and-docker\code\main.py"
```

## Building the image

To tackle this step we only need to run the following command:

```bash
docker build -t jinja-latex .
```

We use the [`docker build` command](https://docs.docker.com/build/building/packaging/#building) to build the image. The `-t` flag is used to indicate the image name and tag, in this example we are setting the name to be `jinja-latex` with no tag. Finally, the dot at the and indicates that the Dockerfile should use the current directory as build context for the image.

!!! warning "Image size"
    Building the image might take a couple of minutes and have a size around 4 GB, which is due to the metapackage texlive-full. To reduce the image size I recommend reading [this Gist](https://gist.github.com/wkrea/b91e3d14f35d741cf6b05e57dfad8faf){:target="_blank"}.


## Running the container

Once the image is built, navigate where the `main.py` file is on your host computer, then run the container with the following command:

```bash
docker run --rm -v "/$(pwd)://code" jinja-latex 
```

The flag [`--rm`](https://docs.docker.com/reference/cli/docker/container/rm/){:target="_blank"} will remove the container after it finishes running since we don't need it anymore, another one can always be built from the image. The `-v "/$(pwd)://code"` flag will map the current working directory on the host computer to the `/code` directory inside the image. Finally, `jinja-latex` instructs docker to build the container using the image with the tag `jinja-latex`.

After a few seconds you should see an output similar to this one:

```bash
This is XeTeX, Version 3.141592653-2.6-0.999995 (TeX Live 2023/Alpine Linux) (preloaded format=xelatex)
 restricted \write18 enabled.
entering extended mode
```

This indicates the xelatex run with no issues. 


## Visualizing the results

Next, check your current directory, there should be some new directories and files:

```text
├── assets
│   └── plots
│       └── pairplot.pgf
├── outputs
│   ├── main.pdf
│   └── main.tex
...
```

Try opening the `main.pdf` file, it should contain something like this:

[latex_output_example]:../../assets/posts/report-generator-with-jinja-latex-and-docker/images/latex_output_example.png

[![latex_output_example]][latex_output_example]


## Adding extra contents to the final pdf

A great feature is that you can edit the `main.tex` file inside the `outputs` directory to customize the text of the final pdf.

To use the feature we can use the followind command:

```bash
docker run -it --entrypoint //bin//bash -v "/$(pwd)://code" --name pdf-generator jinja-latex
```

The `-it` flag is really two flags, the [`i` (interactive) flag](https://docs.docker.com/reference/cli/docker/container/run/#interactive){:target="_blank"} and the [`t` (Allocate a pseudo-TTY) flag](https://docs.docker.com/reference/cli/docker/container/run/#tty){:target="_blank"}. We will use them in combination with the `--entrypoint //bin//bash` to open a bash terminal and pass commands to the container. Finally, we add a name to the container with `--name pdf-generator`.

You should see something like this on the terminal:

```bash
b7b15f4f21cb:/code# 
```

That indicates that the container is waiting for input.


Now we can proceed to add our changes to the `main.tex` file:

```tex
...

\section{Custom section added to the main.tex file}

Some custom content added to the main.tex file directly.

...
```

Then, use xelatex to build the pdf from the `main.tex` file:

```bash title="b7b15f4f21cb:/code#"
xelatex -interaction=batchmode .//outputs//main.tex
```

Next, we can use the `clean` function inside the `main.py` file to reorganize and remove the output files: 

```bash title="b7b15f4f21cb:/code#"
python -c 'import main; main.clean()'
```

After finishing using the container, exit the terminal:

```bash title="b7b15f4f21cb:/code#"
exit
```

And delete the container it using the command:

```bash
docker container rm pdf-generator
```


## Conclusion

In this blog post I showed how you can create high quality pdf files dynamically which could be used to save a lot of time and effort when performing repetitive tasks. Using this method you can create periodic reports updating the plots and statistics really fast and even customizing the output tex file and recreating the pdf.


## Sources

- Denk, T. (2019, August 12). Exporting matplotlib plots to latex. Timo Denk’s Blog. [https://blog.timodenk.com/exporting-matplotlib-plots-to-latex/](https://blog.timodenk.com/exporting-matplotlib-plots-to-latex/){:target="_blank"} 
- Erickson, B. (2015, November 24). Latex templates with python and Jinja2 to generate pdfs. Brad Erickson. [https://13rac1.com/articles/2015/11/latex-templates-python-and-jinja2-generate-pdfs/](https://13rac1.com/articles/2015/11/latex-templates-python-and-jinja2-generate-pdfs/){:target="_blank"}
- Walton, J. (2020, March 24). Matplotlib plots for latex with PGF. It’s more fun to compute. [https://jwalton.info/Matplotlib-latex-PGF/](https://jwalton.info/Matplotlib-latex-PGF/){:target="_blank"} 
