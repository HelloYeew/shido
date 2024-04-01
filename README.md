# 🌱 EndangerEd Project

---

## 📚 Shīdo

### 🔍 Overview
Shīdo is a robust ontological knowledge base that can store and output a wide variety of data. 
It provides an easy way to view, create, update, and delete information through its web interface, 
includes a REST compliant API for interfacing with other modules, and offers a wiki-like view for general reading.

### 📟 Technical Details
Shīdo uses Django as its framework and PostgreSQL for its database. 

The knowledge base, at its core, operates on three main components.

| **Component** | **Description**                                                                                                                                  |
|---------------|--------------------------------------------------------------------------------------------------------------------------------------------------|
| Class         | A class functions as a concept that can be used to group instances together and define what properties they can have.                            |     
| Instance      | An instance represents an entity belonging to a class. It contains defined properties along with wiki properties for constructing the wiki view. | 
| Property      | A property belongs to a class and is concretely defined by the instances of said class.                                                          |

For properties, Shīdo provides many datatypes for storing them. This makes properties highly adaptable.

| **List of Available Property Types** |
|--------------------------------------|
| String                               |
| Number                               |
| Float                                |
| Boolean                              |
| Date                                 |
| DateTime                             |
| Markdown                             |
| Image                                |
| File                                 |
| Instance                             |
| Instance list                        |
| JSON                                 |
| Class                                |
| URL                                  |

Configuring these components is done through forms, which are available on the web interface. Note that this can be done
only if the user is authorized to do such action. As for reading, the wiki views are public and can be found on instance pages.
They are dynamically constructed from the wiki properties of the instances.

A RESTful API is also provided.

| **Method** | **URL**                           | **Parameter** | **Description**                                       |
|------------|-----------------------------------|---------------|-------------------------------------------------------|
| GET        | `/api/class`                      | None          | Lists all classes.                                    |
| GET        | `/api/property_type`              | `class`       | Lists all properties belonging to the provided class. |
| GET        | `/api/instance/<instance_id>`     | None          | Gets the information of the provided instance.        |
| GET        | `/api/instance/random_from_class` | None          | Gets the information of a random instance.            |

### 📥 Installation
1. Clone the repository to your machine using the following command:
```commandline
git clone https://github.com/endangered-project/shido.git 
```
2. Navigate to the project folder.
3. Create your own `.env` file based on the provided example.
3. Setup poetry on your machine by following the tutorial [here](https://python-poetry.org/docs/).
4. All poetry files are already provided, the only thing left is to properly setup poetry virtual environment.
5. Create a poetry virtual environment:
```commandline
poetry shell
```
6. Install dependencies:
```commandline
poetry install
```
7. The project can now be run using the following command:
```commandline
poetry run python manage.py runserver
```

### 📊 Progression
See [GitHub Project](https://github.com/orgs/endangered-project/projects/1/) ([or the old board](https://github.com/users/HelloYeew/projects/8/views/2)).

---

## 🧭 Navigation

#### &emsp;&nbsp; 👉 📚 Shīdo - Platform's Knowledge Base

#### &emsp;&emsp;&emsp; [🗄️ Gameserver - Platform's Server](https://github.com/endangered-project/gameserver)

#### &emsp;&emsp;&nbsp;&nbsp;&nbsp; [🕹️ EndangerEd - Platform's Client](https://github.com/endangered-project/EndangerEd)



