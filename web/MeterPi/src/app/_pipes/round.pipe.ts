import { Pipe, PipeTransform } from '@angular/core';

@Pipe({
  name: 'round'
})
export class RoundPipe implements PipeTransform {

  transform(value: number, ...args: unknown[]): string {
    return value.toFixed(2);
  }

}
