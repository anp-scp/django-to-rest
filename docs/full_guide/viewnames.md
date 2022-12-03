---
title: Nomenclature of default views
---

View names are used for reversing the urls which may be required for difeerent purposes like testing. As the views are created automatically, the view names are created as follows:

* For any model the view-name is created as follows:

    * For detailed view: `<model_label>-<detail>` with all `.` replaced with `_` and all lower cases. For example: if there is an app with name `edu` and a model named `Student` then the view name would be `edu_student-detail`.
    * For list view: `<model_label>-<list>` with all `.` replaced with `_` and all lower cases. For example: if there is an app with name `edu` and a model named `Student` then the view name would be `edu_student-list`.

* For any child model (in relationship with other model) a nested url is created and the view name is generated as follows:

    * For detailed view: `<parent_model_label>-<parent_model_name>-<relatedName>-<detail>` with all `.` replaced with `_` and all lower cases. For example: if there is an app with name `edu` and a model named `Student` with many to many relationship with another model named `Course` then the view name would be `edu_student-student-course_set-detail`.
    * For detailed view: `<parent_model_label>-<parent_model_name>-<relatedName>-<list>` with all `.` replaced with `_` and all lower cases. For example: if there is an app with name `edu` and a model named `Student` with many to many relationship with another model named `Course` then the view name would be `edu_student-student-course_set-list`.

