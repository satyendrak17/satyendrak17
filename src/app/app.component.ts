import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, FormArray, Validators } from '@angular/forms';
@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent implements OnInit{
  title = 'testapp';

  orderForm: FormGroup;
  items: FormArray;

  constructor(private formBuilder: FormBuilder) {
    this.orderForm = this.formBuilder.group({
      customerName: '',
      email: '',
      items: this.formBuilder.array([ this.createItem() ])
    });
  }

  ngOnInit() {
  }

  createItem(): FormGroup {
    return this.formBuilder.group({
      name: [null, Validators.required],
      description: '',
      price: ''
    });
  }

  addItem(): void {
    this.items = this.orderForm.get('items') as FormArray;
    this.items.push(this.createItem());
    // console.log('orderForm.get', this.orderForm.get('items').controls);

    const arrayControl = this.orderForm.get('items') as FormArray;
    console.log('arrayControl ', arrayControl.at(0).value);
    // Print
    // for (let i = 0; i < this.orderForm.controls.items.controls.length; i++) {
    //  const tData = this.orderForm.controls.items[i].
    //  console.log('Names are - ', );
    // }
  }


}
