import { FormRow } from './FormRow';
import { Button } from './Button';

export function FriendRows({ rows, onChange, onAdd, label, addLabel = '+ Add friend' }) {
  return (
    <FormRow label={label}>
      <div className="friend-rows">
        {rows.map((row, i) => (
          <div key={i} className="friend-row">
            <input
              type="text"
              placeholder="Friend name"
              value={row.name}
              onChange={(e) => onChange(i, { ...row, name: e.target.value })}
            />
            <input
              type="text"
              className="amount-input"
              placeholder="0.00"
              value={row.amount}
              onChange={(e) => onChange(i, { ...row, amount: e.target.value })}
            />
          </div>
        ))}
      </div>
      <Button variant="ghost" onClick={onAdd}>
        {addLabel}
      </Button>
    </FormRow>
  );
}
