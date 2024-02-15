class BaseGridManager {

    constructor(settings) {
        this.widgetName = settings.widgetName;
        this.gridTable = document.getElementById(this.widgetName + '-table');
    }

    addCell(row) {
        let cell = row.insertCell();
        let input = document.createElement("input");
        input.setAttribute('type', 'text');
        input.setAttribute('name', this.widgetName);
        input.setAttribute('size', '2');
        input.setAttribute('required', 'true');
        cell.appendChild(input);
    }

    updateCells(row, dim) {
        for (let i = 0; i < Math.max(dim, row.cells.length); i++) {
            if (i < dim) {
                if (row.cells[i] === undefined) {
                    this.addCell(row);
                }
            }
            else {
                if (row.cells[i] !== undefined) {
                    row.deleteCell(i);
                }
            }
        }
    }

}

class GridManager extends BaseGridManager {

    constructor(settings) {
        super(settings);
        this.widthField = document.getElementById(this.widgetName + '-width')
        this.addRowButton = document.getElementById(this.widgetName + '-add-row');
        this.deleteRowButton = document.getElementById(this.widgetName + '-delete-row');
        this.minWidth = settings.minWidth;
        this.maxWidth = settings.maxWidth;
        this.minHeight = settings.minHeight;
        this.maxHeight = settings.maxHeight;
    }

    init() {
        let self = this;

        this.widthField.addEventListener("change", function (el) {
            el.preventDefault();
            for (let i = 0; i < self.gridTable.rows.length; i++) {
                let row = self.gridTable.rows[i];
                let width = parseInt(self.widthField.value, 10);
                self.updateCells(row, width);
            }
        });

        if (this.addRowButton) {
            this.addRowButton.addEventListener("click", function(el) {
                el.preventDefault();
                let row = self.gridTable.insertRow();
                let width = parseInt(self.widthField.value, 10);
                for (let i = 0; i < width; i++) {
                    self.addCell(row);
                }
                self.checkLinksState();
            });
        }
        if (this.deleteRowButton) {
            this.deleteRowButton.addEventListener("click", function(el) {
                el.preventDefault();
                self.gridTable.deleteRow(-1);
                self.checkLinksState();
            });
        }
        this.checkLinksState();
    }

    checkLinksState() {
        if (this.addRowButton) {
            this.addRowButton.classList.remove("disabled");
            if (this.gridTable.rows.length === this.maxHeight) {
                this.addRowButton.classList.add("disabled");
            }
        }
        if (this.deleteRowButton) {
            this.deleteRowButton.classList.remove("disabled");
            if (this.gridTable.rows.length === this.minHeight) {
                this.deleteRowButton.classList.add("disabled");
            }
        }
    }

}

class SquareGridManager extends BaseGridManager {

    constructor(settings) {
        super(settings);
        this.sizeField = document.getElementById(this.widgetName + '-size');
    }

     init() {
         let self = this;

         this.sizeField.addEventListener("change", function (el) {
             el.preventDefault();
             let size = parseInt(this.value, 10);
             for (let i = 0; i < Math.max(size, self.gridTable.rows.length); i++) {
                 let row = self.gridTable.rows[i];
                 if (row === undefined) {
                     if (i < size) {
                         let newRow = self.gridTable.insertRow();
                         for (let ii = 0; ii < size; ii++) {
                             self.addCell(newRow);
                         }
                     }
                 }
                 else {
                     if (i < size) {
                         self.updateCells(row, size);
                     }
                     else {
                         self.gridTable.deleteRow(i);
                     }
                 }
             }
         });
     }

}