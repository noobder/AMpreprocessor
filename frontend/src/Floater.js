import React from 'react'

const Floater = () => {
  return (
    <div><div className="floating-formula">y = mx + b</div>
    <div className="floating-formula">θ = θ - α ∂J/∂θ</div>
    <div className="floating-formula">J(θ) = 1/2m Σ (hθ(x) - y)²</div>
    <div className="floating-formula">σ(x) = 1 / (1 + e⁻ˣ)</div>
    <div className="floating-formula">σ(zᵢ) = e^(zᵢ) / Σ e^(zⱼ)</div>
    <div className="floating-formula">L = - Σ y log(ŷ)</div>
    <div className="floating-formula">P(A|B) = P(B|A) P(A) / P(B)</div></div>
  )
}

export default Floater